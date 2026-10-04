using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Security.Cryptography;

internal static class RuntimeBootstrap {
    internal const string PythonUrl = "https://www.python.org/ftp/python/3.13.16/python-3.13.16-embed-amd64.zip";
    internal const string PythonHash = "97dae5274cc54867065e8d5a3226e48c35017ed332a0fdb0e27d5b5821961297";
    internal const string NodeUrl = "https://nodejs.org/dist/v22.23.3/node-v22.23.3-win-x64.zip";
    internal const string NodeHash = "2b0ff57b049cda1bbcea2240eec20467018713c1efe1f7360c2681859b90ed71";
    internal static string Probe(string executable, bool python, string prefix = "") {
        try {
            var args = python ? "-c \"import sys,ssl,urllib.request; assert (3,10)<=sys.version_info[:2]<(4,0); print(sys.executable)\"" : "-e \"if(Number(process.versions.node.split('.')[0])<22||typeof WebSocket!=='function'||typeof fetch!=='function')process.exit(1);console.log(process.execPath)\"";
            var info = new ProcessStartInfo(executable, prefix + args) { UseShellExecute=false, CreateNoWindow=true, RedirectStandardOutput=true, RedirectStandardError=true };
            using (var process = Process.Start(info)) {
                if (!process.WaitForExit(5000)) { process.Kill(); return null; }
                string path = process.StandardOutput.ReadToEnd().Trim();
                return process.ExitCode==0 && File.Exists(path) ? path : null;
            }
        } catch { return null; }
    }
    internal static string CommandPath(string command) {
        if(Path.IsPathRooted(command))return File.Exists(command)?command:null;
        foreach(string folder in (Environment.GetEnvironmentVariable("PATH")??"").Split(Path.PathSeparator)) {
            try {
                string path=Path.Combine(folder.Trim('"'),command);
                // Store execution aliases can open the Store instead of a runtime.
                if(path.IndexOf("\\WindowsApps\\",StringComparison.OrdinalIgnoreCase)<0&&File.Exists(path))return path;
            } catch {}
        }
        return null;
    }
    internal static string Find(string root, string cache, bool python) {
        string name = python ? "python" : "node";
        string bundled = Path.Combine(root,"runtime",name,name+".exe");
        if (File.Exists(bundled)) { string value=Probe(bundled,python); if(value!=null)return value; }
        foreach(string command in python ? new[]{"python.exe","python3.exe","py.exe"} : new[]{"node.exe",Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),"nodejs","node.exe")}) {
            string path=CommandPath(command);
            if(path==null)continue;
            string value=Probe(path,python,command=="py.exe"?"-3 ":""); if(value!=null)return value;
        }
        string cached = Path.Combine(cache,name,name+".exe");
        return File.Exists(cached) ? Probe(cached,python) : null;
    }
    internal static string Install(string cache, bool python, Action<string,int> progress, Func<bool> cancelled) {
        string name=python?"python":"node", url=python?PythonUrl:NodeUrl, expected=python?PythonHash:NodeHash;
        Directory.CreateDirectory(cache);
        string archive=Path.Combine(cache,name+"-"+Guid.NewGuid()+".zip"), stage=archive+".stage", target=Path.Combine(cache,name);
        try {
            ServicePointManager.SecurityProtocol |= SecurityProtocolType.Tls12;
            progress("正在下载 / Downloading "+name,0);
            var request=(HttpWebRequest)WebRequest.Create(url); request.Timeout=30000; request.ReadWriteTimeout=30000;
            using(var response=request.GetResponse()) using(var input=response.GetResponseStream()) using(var output=File.Create(archive)) {
                byte[] buffer=new byte[65536];long done=0;int count;
                while((count=input.Read(buffer,0,buffer.Length))>0) {
                    if(cancelled())throw new OperationCanceledException();
                    output.Write(buffer,0,count);done+=count;
                    progress("正在下载 / Downloading "+name,response.ContentLength>0?(int)(done*100/response.ContentLength):0);
                }
            }
            progress("校验并准备 / Verifying "+name,100);
            using(var sha=SHA256.Create()) using(var input=File.OpenRead(archive)) {
                string hash=BitConverter.ToString(sha.ComputeHash(input)).Replace("-","").ToLowerInvariant();
                if(hash!=expected)throw new Exception("下载校验失败，请重试。 / Download checksum mismatch. Please retry.");
            }
            if(cancelled())throw new OperationCanceledException();
            Directory.CreateDirectory(stage);
            if(python) {
                ZipFile.ExtractToDirectory(archive,stage);
                // Isolated cache must import this installation's app modules via the launcher.
                File.WriteAllText(Path.Combine(stage,"python313._pth"),"python313.zip\n.\nimport site\n");
            } else {
                // Only node.exe and its license are needed, not npm.
                using(var zip=ZipFile.OpenRead(archive)) foreach(var entry in zip.Entries) {
                    string leaf=Path.GetFileName(entry.FullName);
                    if(entry.FullName.Split('/').Length==2 && (leaf=="node.exe" || leaf=="LICENSE"))entry.ExtractToFile(Path.Combine(stage,leaf));
                }
            }
            string exe=Path.Combine(stage,name+".exe");
            if(Probe(exe,python)==null)throw new Exception("运行环境验证失败 / Runtime validation failed: "+name);
            if(Directory.Exists(target))Directory.Delete(target,true);
            Directory.Move(stage,target);
            return Path.Combine(target,name+".exe");
        } finally {
            if(File.Exists(archive))File.Delete(archive);
            if(Directory.Exists(stage))Directory.Delete(stage,true);
        }
    }
}
