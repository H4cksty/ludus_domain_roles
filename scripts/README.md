<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>README - Ludus Config Builder</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #111827;
            color: #d1d5db;
        }
        h1, h2, h3 {
            font-family: 'Roboto Mono', monospace;
            color: #ffffff;
        }
        code {
            background-color: #1f2937;
            color: #9ca3af;
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 0.9em;
            border-radius: 0.25rem;
            font-family: 'Roboto Mono', monospace;
        }
        pre > code {
            display: block;
            padding: 1em;
            border-radius: 0.5rem;
        }
        .container {
            max-width: 48rem;
            margin: auto;
        }
        .pro-tip {
            background-color: rgba(59, 130, 246, 0.1);
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            border-radius: 0.25rem;
        }
    </style>
</head>
<body class="p-4 sm:p-6 md:p-8">
    <div class="container">
        <header class="mb-8">
            <h1 class="text-4xl font-bold tracking-tight">Ludus Config Builder Script</h1>
            <p class="mt-2 text-lg text-gray-400">An interactive command-line wizard for generating complex `ludus-config.yml` files.</p>
        </header>

        <section class="mb-8">
            <h2 class="text-2xl font-bold border-b border-gray-700 pb-2 mb-4">Overview</h2>
            <p>This Python script provides a guided, interactive experience for creating sophisticated `ludus-config.yml` files that leverage the `ludus_forest_build_roles` collection. It automates the most error-prone parts of the configuration process, ensuring that all custom roles are used correctly and that the resulting lab environment is robust and reliable.</p>
        </section>

        <section class="mb-8">
            <h2 class="text-2xl font-bold border-b border-gray-700 pb-2 mb-4">Key Features</h2>
            <ul class="list-disc list-inside space-y-2">
                <li><strong>Interactive Wizard:</strong> Guides the user through every step of the lab design, from global defaults to individual VM configurations.</li>
                <li><strong>Dynamic Lookups:</strong> Automatically fetches available Ludus templates and verifies that the required Ansible roles are installed on the system.</li>
                <li><strong>Automated Role Installation:</strong> If required roles are missing, the script can find them within your home directory (assuming the project is cloned there) and install them automatically.</li>
                <li><strong>Intelligent Defaults:</strong> Offers the option to use pre-configured, sensible defaults to speed up the configuration process.</li>
                <li><strong>Post-Generation Actions:</strong> After creating the `ludus-config.yml` file, provides a menu to immediately set the config, deploy the range, and monitor its status.</li>
            </ul>
        </section>

        <section class="mb-8">
            <h2 class="text-2xl font-bold border-b border-gray-700 pb-2 mb-4">Prerequisites</h2>
            <ol class="list-decimal list-inside space-y-2">
                <li><strong>Python 3.9+</strong> installed on your system.</li>
                <li>The <strong>PyYAML</strong> library. You can install it via pip:
                    <pre><code class="language-bash">pip install pyyaml</code></pre>
                </li>
                <li>The <strong>Ludus CLI</strong> must be installed and configured in your system's PATH.</li>
                <li>The `ludus_forest_build_roles` repository should be cloned to your home directory or the directory from which you run the script.</li>
            </ol>
        </section>

        <section>
            <h2 class="text-2xl font-bold border-b border-gray-700 pb-2 mb-4">How to Use</h2>
            <ol class="list-decimal list-inside space-y-4">
                <li>
                    <p>Save the script as `build_ludus_config.py` on your machine.</p>
                </li>
                <li>
                    <p>Open your terminal or command prompt, navigate to the directory where you saved the file, and make it executable:</p>
                    <pre><code class="language-bash">chmod +x build_ludus_config.py</code></pre>
                </li>
                <li>
                    <p>Run the script:</p>
                    <pre><code class="language-bash">./build_ludus_config.py</code></pre>
                </li>
                <li>
                    <p>Follow the on-screen prompts. The script will ask for all necessary information, such as the output filename, your Ludus range ID, and details for each domain and virtual machine you wish to create.</p>
                </li>
                <li class="pro-tip">
                    <h3 class="font-bold text-white mb-1">Pro Tip:</h3>
                    <p>For the fastest experience, accept the default values when prompted (by pressing Enter), especially for the "Global Default Settings." This will quickly generate a standard, functional configuration.</p>
                </li>
                <li>
                    <p>Once the `generated-config.yml` (or your custom filename) is created, the script will present a menu with options to set the config, deploy the range, or exit.</p>
                </li>
            </ol>
        </section>

    </div>
</body>
</html>
