const { getRepoFiles } = require("../services/githubService");
const { analyzeCode } = require("../services/qualityService");

async function verifyMilestone(req, res) {

try {

const { repoLink, milestone } = req.body;

const repoData = await getRepoFiles(repoLink);

const result = await analyzeCode(
    milestone,
    repoData.structure,
    repoData.code
);

res.json({
result
});

} catch (error) {

console.log(error);

res.status(500).json({
error: "Quality check failed"
});

}

}

module.exports = { verifyMilestone };