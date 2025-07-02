<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ludus Forest Build Roles README</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            line-height: 1.5;
            color: #e6edf3;
            background-color: #0d1117;
            padding: 2rem;
        }
        .container {
            max-width: 800px;
            margin: auto;
        }
        h1, h2, h3 {
            font-weight: 600;
            border-bottom: 1px solid #30363d;
            padding-bottom: 0.3em;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        h1 { font-size: 2em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.25em; }
        p, ul, ol {
            margin-bottom: 16px;
        }
        ul, ol {
            padding-left: 2em;
        }
        code {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
            background-color: rgba(110,118,129,0.4);
            padding: .2em .4em;
            font-size: 85%;
            border-radius: 6px;
        }
        pre {
            background-color: #161b22;
            padding: 16px;
            border-radius: 6px;
            overflow: auto;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        a {
            color: #58a6ff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ludus Config Builder Script</h1>
        <p>An interactive command-line wizard for generating complex <code>ludus-config.yml</code> files.</p>
        
        <h2>Overview</h2>
        <p>This Python script provides a guided, interactive experience for creating sophisticated <code>ludus-config.yml</code> files that leverage the <code>ludus_forest_build_roles</code> collection. It automates the most error-prone parts of the configuration process, ensuring that all custom roles are used correctly and that the resulting lab environment is robust and reliable.</p>
        
        <h2>Key Features</h2>
        <ul>
            <li><strong>Interactive Wizard:</strong> Guides the user through every step of the lab design, from global defaults to individual VM configurations.</li>
            <li><strong>Dynamic Lookups:</strong> Automatically fetches available Ludus templates and verifies that the required Ansible roles are installed on the system.</li>
            <li><strong>Automated Role Installation:</strong> If required roles are missing, the script can find them within your home directory (assuming the project is cloned there) and install them automatically.</li>
            <li><strong>Intelligent Defaults:</strong> Offers the option to use pre-configured, sensible defaults to speed up the configuration process.</li>
            <li><strong>Post-Generation Actions:</strong> After creating the <code>ludus-config.yml</code> file, provides a menu to immediately set the config, deploy the range, and monitor its status.</li>
        </ul>
        
        <h2>Prerequisites</h2>
        <ol>
            <li><strong>Python 3.9+</strong> installed on your system.</li>
            <li>The <strong>PyYAML</strong> library. You can install it via pip:
                <pre><code class="language-bash">pip install pyyaml</code></pre>
            </li>
            <li>The <strong>Ludus CLI</strong> must be installed and configured in your system's PATH.</li>
            <li>The <code>ludus_forest_build_roles</code> repository should be cloned to your home directory or the directory from which you run the script.</li>
        </ol>
        
        <h2>How to Use</h2>
        <ol>
            <li>Save the script as <code>build_ludus_config.py</code> on your machine.</li>
            <li>Open your terminal or command prompt, navigate to the directory where you saved the file, and make it executable:
                <pre><code class="language-bash">chmod +x build_ludus_config.py</code></pre>
            </li>
            <li>Run the script:
                <pre><code class="language-bash">./build_ludus_config.py</code></pre>
            </li>
            <li>Follow the on-screen prompts. The script will ask for all necessary information, such as the output filename, your Ludus range ID, and details for each domain and virtual machine you wish to create.</li>
            <li><strong>Pro Tip:</strong> For the fastest experience, accept the default values when prompted (by pressing Enter), especially for the "Global Default Settings." This will quickly generate a standard, functional configuration.</li>
            <li>Once the <code>generated-config.yml</code> (or your custom filename) is created, the script will present a menu with options to set the config, deploy the range, or exit.</li>
        </ol>
    </div>
</body>
</html>
