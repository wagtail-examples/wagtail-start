from pathlib import Path
from pydoc import cli
import subprocess

import click

webpack_content = """const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const BrowserSyncPlugin = require("browser-sync-webpack-plugin");

module.exports = {
  mode: "production", // or "development"
  entry: path.resolve(__dirname, "./client/scripts/index.js"),
  output: {
    path: path.resolve(__dirname, "./webapp/static/webapp"),
    filename: "bundle.js",
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env"],
          },
        },
      },
      {
        test: /\.scss$/,
        use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "bundle.css",
    }),
    new BrowserSyncPlugin({
      host: "localhost",
      port: 3000,
      proxy: "http://127.0.0.1:8000/", // the port your django app will be running on in development
      files: ["./**/*.html"],
    }),
  ],
};"""

def generate_frontend(working_dir, path, package_name, cwd, ignore_append):
    """Generate webpack setup
    by creating the webpack config and moving files around

    Args:
        working_dir (Path): The path to the package directory
        path (Path): The path to the site directory
        package_name (str): The name of the package
        cwd (Path): The path to this apps root directory
    """

    # CLIENT
    subprocess.run(["mkdir", "-p", "client/scripts"], cwd=path, check=True)
    subprocess.run(["mkdir", "-p", "client/styles"], cwd=path, check=True)
    with open(path / "client/styles/index.scss", "w") as f:
        f.write("""body { background-color: #fff; color: #000; }""")
    with open(path / "client/scripts/index.js", "w") as f:
        f.write("""import "../styles/index.scss";\nconsole.log("hello world");""")

    # TEMPLATES
    with open(working_dir / "templates" / "base.html", "r") as f:
        content = f.read()
        content = content.replace(
            "'css/webapp.css'", f"'{package_name}/bundle.css'"
        )
        content = content.replace(
            "'js/webapp.js'", f"'{package_name}/bundle.js'"
        )
    with open(working_dir / "templates" / "base.html", "w") as f:
        f.write(content)

    # REMOVE STATIC
    subprocess.run(
        ["rm", "-rf", str(working_dir / "home" / "static")],
    )
    subprocess.run(["rm", "-rf", str(working_dir / "static" / "css")])
    subprocess.run(["rm", "-rf", str(working_dir / "static" / "js")])

        # GIT IGNORE
    append_line = "\n# node\nnode_modules\n"

    if ignore_append:
        with open(path / ".gitignore", "r") as f:
            content = f.read()
            if append_line not in content:
                content += append_line
                with open(path / ".gitignore", "w") as f:
                    f.write(content)
    else:
        with open(path / ".gitignore", "a") as f:
            f.write(append_line)

    # NPM
    subprocess.run(
        ["npm", "init", "-y"], cwd=path, check=True, stdout=subprocess.DEVNULL
    )
    with open(path / ".nvmrc", "w") as f:
        f.write("18")

    dev_packages = [
        "@babel/preset-env",
        "babel-loader",
        "browser-sync-webpack-plugin",
        "css-loader",
        "mini-css-extract-plugin",
        "sass",
        "sass-loader",
        "webpack",
        "webpack-cli",
        "webpack-dev-server",
    ]
    subprocess.run(
        ["npm", "install", "--package-lock-only", *dev_packages, "--save-dev"],
        cwd=path,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    with open(path / "package.json", "r") as f:
        content = f.read()
        content = content.replace(
            '"test": "echo \\"Error: no test specified\\" && exit 1"',
            '"build": "webpack --mode production",\n    "start": "webpack --mode development --watch"',
        )
    with open(path / "package.json", "w") as f:
        f.write(content)

    # WEBPACK CONFIG
    with open(path / "webpack.config.js", "w") as f:
        f.write(webpack_content.replace("webapp", package_name))


