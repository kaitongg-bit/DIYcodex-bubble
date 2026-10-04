using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

internal static class Launcher {
    [STAThread]
    private static int Main(string[] args) {
        try {
            string root = AppDomain.CurrentDomain.BaseDirectory;
            if(Array.IndexOf(args,"--uninstall-startup")>=0) {
                string startup=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Startup),"DIY Codex Bubble Restore.vbs");
                if(File.Exists(startup)&&File.ReadAllText(startup).Contains(root.TrimEnd(Path.DirectorySeparatorChar)))File.Delete(startup);
                return 0;
            }
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
            info.WorkingDirectory=root;info.UseShellExecute=false;info.CreateNoWindow=true;info.RedirectStandardError=true;
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
