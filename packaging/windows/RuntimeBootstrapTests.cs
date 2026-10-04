using System;
using System.IO;
internal static class RuntimeBootstrapTests {
    static int Main(string[] args) {
        string root=args[0],cache=args[1];
        string startup=cache+"-startup.vbs";
        File.WriteAllText(startup,"Set shell = CreateObject(\"WScript.Shell\")\r\n"+root+"\\scripts\\login-start.py");
        Launcher.MigrateStartup(root,startup);
        if(!File.ReadAllText(startup).Contains("DIY Codex Bubble.exe")||File.ReadAllText(startup).Contains("login-start.py"))throw new Exception("Legacy startup migration failed");
        File.WriteAllText(startup,"Unrelated startup entry");Launcher.MigrateStartup(root,startup);
        if(File.ReadAllText(startup)!="Unrelated startup entry")throw new Exception("Unrelated startup modified");
        File.Delete(startup);
        // A new light package must have no bundled runtimes.
        if(Directory.Exists(Path.Combine(root,"runtime")))throw new Exception("Light build bundles runtimes");
        if(RuntimeBootstrap.Probe("cmd.exe",true)!=null)throw new Exception("Invalid Python accepted");
        string python=RuntimeBootstrap.Find(root,cache,true),node=RuntimeBootstrap.Find(root,cache,false);
        if(python==null||node==null)throw new Exception("Existing compatible runtimes not reused");
        if(Directory.Exists(cache))throw new Exception("Reuse unexpectedly installed runtimes");
        // Exercise the same verified download/extraction used on a fresh machine.
        string isolated=cache+"-fresh";
        string p=RuntimeBootstrap.Install(isolated,true,(m,n)=>{},()=>false);
        string npath=RuntimeBootstrap.Install(isolated,false,(m,n)=>{},()=>false);
        if(RuntimeBootstrap.Probe(p,true)==null||RuntimeBootstrap.Probe(npath,false)==null)throw new Exception("Downloaded runtimes failed validation");
        File.WriteAllText(Path.Combine(isolated,"python","python313._pth"),"python313.zip\n.\n"+Path.Combine(root,"app")+"\n"+root+"\n");
        var info=new System.Diagnostics.ProcessStartInfo(p,"-X utf8 -c \"import server,autostart,ssl\"") { UseShellExecute=false,CreateNoWindow=true };
        info.EnvironmentVariables["PYTHONDONTWRITEBYTECODE"]="1";
        info.EnvironmentVariables["BUBBLE_STUDIO_DATA"]=Path.Combine(isolated,"test-data");
        using(var process=System.Diagnostics.Process.Start(info)) { process.WaitForExit();if(process.ExitCode!=0)throw new Exception("Cached Python cannot import the workshop"); }
        Console.WriteLine("Reused compatible runtimes; downloaded and verified missing Python and Node.");
        return 0;
    }
}
