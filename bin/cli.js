#!/usr/bin/env node
/**
 * ipgeolocationapi.io MCP server - Node.js distribution wrapper.
 * Runs the Python MCP server over stdio. Install with:
 *   npx -y @ipgeolocationapi/mcp
 * First run creates a small Python venv (one time) on macOS/Linux.
 */
const { spawn, spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const key = process.env.IPGEO_API_KEY || "";
const base = process.env.IPGEO_BASE || "https://ipgeolocationapi.io";
const script = path.join(__dirname, "..", "mcp_server.py");

const env = Object.assign({}, process.env, {
  IPGEO_API_KEY: key,
  IPGEO_BASE: base,
  PYTHONUNBUFFERED: "1",
});
// never let a host PYTHONPATH leak into the child interpreter (breaks pip + imports)
delete env.PYTHONPATH;

function run(py, args) {
  return spawnSync(py, args, { encoding: "utf8", env });
}

function pickPython() {
  const candidates = [process.env.IPGEO_PYTHON, "python3", "python"].filter(Boolean);
  for (const c of candidates) {
    const r = run(c, ["-c", "import sys; print(1 if sys.version_info >= (3, 10) else 0)"]);
    if (r.status === 0 && r.stdout.trim() === "1") return c;
  }
  console.error("ipgeolocationapi mcp: no Python 3.10+ found. Install python3 or set IPGEO_PYTHON.");
  process.exit(1);
}

function hasDeps(py) {
  return run(py, ["-c", "import mcp, httpx"]).status === 0;
}

const py = pickPython();

let child;
if (hasDeps(py)) {
  child = spawn(py, [script], { env, stdio: "inherit" });
} else {
  const home = path.join(os.homedir(), ".ipgeolocationapi-mcp");
  const venv = path.join(home, "venv");
  const isWin = process.platform === "win32";
  const pyBin = isWin ? path.join(venv, "Scripts", "python.exe") : path.join(venv, "bin", "python");
  if (!fs.existsSync(pyBin)) {
    console.error("ipgeolocationapi mcp: first run, preparing runtime (one time)...");
    fs.mkdirSync(home, { recursive: true });
    const v1 = run(py, ["-m", "venv", venv]);
    if (v1.status !== 0) {
      console.error("ipgeolocationapi mcp: venv creation failed:", v1.stderr && v1.stderr.slice(0, 200));
      process.exit(1);
    }
    const v2 = run(pyBin, ["-m", "pip", "install", "-q", "--no-cache-dir", "mcp==1.26.0", "httpx"]);
    if (v2.status !== 0) {
      console.error("ipgeolocationapi mcp: dependency install failed:", v2.stderr && v2.stderr.slice(0, 200));
      process.exit(1);
    }
  }
  child = spawn(pyBin, [script], { env, stdio: "inherit" });
}

child.on("exit", (code) => process.exit(code || 0));
