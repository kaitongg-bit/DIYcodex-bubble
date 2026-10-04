using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

internal static class Launcher {
    internal static bool IsOwnedProcess(string root, string executable, string command) {
        if(string.IsNullOrEmpty(executable)||string.IsNullOrEmpty(command))return false;
        string name=Path.GetFileName(executable).ToLowerInvariant();
        if(name!="python.exe"&&name!="pythonw.exe"&&name!="node.exe")return false;
        foreach(string script in new[]{"app/server.py","scripts/login-start.py","app/bridge.mjs"}) {
            string path=Path.Combine(root,script.Replace('/',Path.DirectorySeparatorChar));
            if(command.Replace('/',Path.DirectorySeparatorChar).IndexOf("\""+path+"\"",StringComparison.OrdinalIgnoreCase)>=0 ||
               command.Replace('/',Path.DirectorySeparatorChar).IndexOf(" "+path+" ",StringComparison.OrdinalIgnoreCase)>=0 ||
               command.Replace('/',Path.DirectorySeparatorChar).EndsWith(" "+path,StringComparison.OrdinalIgnoreCase))return true;
        }
        return false;
    }
    internal static void StopOwnedService(string root) {
        root=Path.GetFullPath(root);
        if(!File.Exists(Path.Combine(root,"app","server.py")))return;
        using(var search=new System.Management.ManagementObjectSearcher("SELECT ProcessId, ExecutablePath, CommandLine FROM Win32_Process WHERE Name='python.exe' OR Name='pythonw.exe' OR Name='node.exe'"))
        using(var items=search.Get()) foreach(System.Management.ManagementObject item in items) {
            using(item) {
                if(!IsOwnedProcess(root,item["ExecutablePath"] as string,item["CommandLine"] as string))continue;
                try { using(var process=Process.GetProcessById(Convert.ToInt32(item["ProcessId"]))) {
                    process.Kill();if(!process.WaitForExit(5000))throw new Exception("工坊后台服务未能退出 / Workshop service did not exit");
                }} catch(ArgumentException) {} // The short-lived bridge may have exited already.
                catch(InvalidOperationException) {} // It exited between lookup and termination.
            }
        }
    }
    internal static void MigrateStartup(string root, string startup) {
        if(!File.Exists(startup))return;
        string content=File.ReadAllText(startup);
        if(content.Contains(root.TrimEnd(Path.DirectorySeparatorChar))&&content.Contains("login-start.py")&&content.Contains("WScript.Shell")) {
            string command="\""+Path.Combine(root,"DIY Codex Bubble.exe")+"\" --restore";
            File.WriteAllText(startup,"Set shell = CreateObject(\"WScript.Shell\")\r\nshell.Run \""+command.Replace("\"","\"\"")+"\", 0, False\r\n",System.Text.Encoding.Unicode);
        }
    }
    [STAThread]
    private static int Main(string[] args) {
        try {
            string root = AppDomain.CurrentDomain.BaseDirectory;
            if(args.Length==2&&args[0]=="--stop-owned-service") { StopOwnedService(args[1]);return 0; }
            if(Array.IndexOf(args,"--uninstall-startup")>=0) {
                StopOwnedService(root);
                string startup=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Startup),"DIY Codex Bubble Restore.vbs");
                if(File.Exists(startup)&&File.ReadAllText(startup).Contains(root.TrimEnd(Path.DirectorySeparatorChar)))File.Delete(startup);
                return 0;
            }
            MigrateStartup(root,Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Startup),"DIY Codex Bubble Restore.vbs"));
            string script = Path.Combine(root,"scripts","login-start.py");
            if(!File.Exists(script))throw new Exception("安装文件不完整，请重新安装。 / Installation files are missing. Please reinstall.");
            string basePath=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"DIY Codex Bubble");
            string data=Path.Combine(basePath,"Data"),cache=Path.Combine(basePath,"Runtime");
            Directory.CreateDirectory(data);
            string python=null,node=null;
            using(var mutex=new Mutex(false,"Local\\DIYCodexBubbleRuntime")) {
                if(!mutex.WaitOne(1000))throw new Exception("工坊正在准备，请稍候。 / The workshop is preparing. Please wait.");
                try {
                    python=RuntimeBootstrap.Find(root,cache,true);node=RuntimeBootstrap.Find(root,cache,false);
                    if(python==null||node==null) {
                        Application.EnableVisualStyles();
                        var form=new Form { Text="DIY Codex Bubble",Width=500,Height=190,StartPosition=FormStartPosition.CenterScreen,FormBorderStyle=FormBorderStyle.FixedDialog,MaximizeBox=false };
                        var label=new Label { Left=20,Top=20,Width=450,Height=55,Text="首次准备：只下载缺少的环境。\nFirst setup: downloading only missing runtimes." };
                        var bar=new ProgressBar { Left=20,Top=85,Width=445,Height=24 };
                        form.Controls.Add(label);form.Controls.Add(bar);
                        bool cancelled=false,finished=false;Exception failure=null;
                        form.FormClosing+=(s,e)=>{ if(!finished){cancelled=true;e.Cancel=true;label.Text="正在取消 / Cancelling…";} };
                        Action<string,int> progress=(message,percent)=>form.BeginInvoke((Action)(()=>{label.Text=message+"\n"+percent+"% · 可关闭窗口取消 / Close to cancel";bar.Value=Math.Max(0,Math.Min(100,percent));}));
                        form.Shown+=(s,e)=>Task.Run(()=>{
                            try {
                                if(python==null)python=RuntimeBootstrap.Install(cache,true,progress,()=>cancelled);
                                if(node==null)node=RuntimeBootstrap.Install(cache,false,progress,()=>cancelled);
                            } catch(Exception error){failure=error;}
                            form.BeginInvoke((Action)(()=>{finished=true;form.Close();}));
                        });
                        Application.Run(form);
                        if(failure is OperationCanceledException)return 0;
                        if(failure!=null)throw new Exception("准备失败，请检查网络后重新打开。也可下载完整离线版。\nSetup failed. Reopen to retry, or download the full offline build.\n"+failure.Message);
                    }
                } finally {mutex.ReleaseMutex();}
            }
            if(string.Equals(python,Path.Combine(cache,"python","python.exe"),StringComparison.OrdinalIgnoreCase))
                File.WriteAllText(Path.Combine(cache,"python","python313._pth"),"python313.zip\n.\n"+Path.Combine(root,"app")+"\n"+root+"\n");
            bool restore=Array.IndexOf(args,"--restore")>=0;
            // Adding the app directory explicitly also works with isolated embedded Python.
            string command="import runpy,sys; sys.path.insert(0,sys.argv[1]); sys.argv=sys.argv[2:]; runpy.run_path(sys.argv[0],run_name='__main__')";
            var info=new ProcessStartInfo(python,"-X utf8 -c \""+command+"\" \""+Path.Combine(root,"app")+"\" \""+script+"\""+(restore?"":" --studio"));
            info.WorkingDirectory=root;info.UseShellExecute=false;info.CreateNoWindow=true;info.RedirectStandardError=true;info.StandardErrorEncoding=System.Text.Encoding.UTF8;
            info.EnvironmentVariables["BUBBLE_STUDIO_DATA"]=data;
            info.EnvironmentVariables["BUBBLE_STUDIO_NODE"]=node;
            using(var process=Process.Start(info)) {
                string error=process.StandardError.ReadToEnd();process.WaitForExit();
                if(process.ExitCode!=0)throw new Exception(error+"\n\n日志 / Logs: "+data);
            }
            return 0;
        } catch(Exception error) {MessageBox.Show(error.Message,"DIY Codex Bubble",MessageBoxButtons.OK,MessageBoxIcon.Error);return 1;}
    }
}
