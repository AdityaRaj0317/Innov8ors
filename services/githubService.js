const axios = require("axios");

async function getRepoFiles(repoLink) {

    const parts = repoLink.replace("https://github.com/", "").split("/");
    const owner = parts[0];
    const repo = parts[1];

    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/git/trees/main?recursive=1`;

    const response = await axios.get(apiUrl);

    const files = response.data.tree;

    let structure = "";
    let code = "";

    for (let file of files) {

        if (file.path.endsWith(".js") ||
            file.path.endsWith(".java") ||
            file.path.endsWith(".py")) {

            structure += file.path + "\n";

            try {

                const rawUrl = `https://raw.githubusercontent.com/${owner}/${repo}/main/${file.path}`;

                const fileContent = await axios.get(rawUrl);

                code += `\nFILE: ${file.path}\n`;
                code += fileContent.data.substring(0, 1500);

            } catch (err) {}

        }
    }

    return { structure, code };

}

module.exports = { getRepoFiles };