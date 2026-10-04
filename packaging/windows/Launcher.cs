using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

internal static class Launcher {
    [STAThread]
    private static int Main(string[] args) {
        try {
            string root = AppDomain.CurrentDomain.BaseDirectory;
            string python = Path.Combine(root, "runtime", "python", "python.exe");
            string script = Path.Combine(root, "scripts", "login-start.py");
            if (!File.Exists(python) || !File.Exists(script))
                throw new Exception("安装文件不完整，请重新安装。 / Installation files are missing. Please reinstall.");
            string data = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "DIY Codex Bubble", "Data");
            Directory.CreateDirectory(data);
            bool restore = Array.IndexOf(args, "--restore") >= 0;
            var info = new ProcessStartInfo(python, "-X utf8 \"" + script + "\"" + (restore ? "" : " --studio"));
            info.WorkingDirectory = root;
            info.UseShellExecute = false;
            info.CreateNoWindow = true;
            info.RedirectStandardError = true;
            info.EnvironmentVariables["BUBBLE_STUDIO_DATA"] = data;
            info.EnvironmentVariables["BUBBLE_STUDIO_NODE"] = Path.Combine(root, "runtime", "node", "node.exe");
            using (var process = Process.Start(info)) {
                string error = process.StandardError.ReadToEnd();
                process.WaitForExit();
                if (process.ExitCode != 0) throw new Exception(error + "\n\n日志 / Logs: " + data);
            }
            return 0;
        } catch (Exception error) {
            MessageBox.Show(error.Message, "DIY Codex Bubble", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}
