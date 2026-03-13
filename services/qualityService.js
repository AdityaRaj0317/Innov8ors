const { GoogleGenerativeAI } = require("@google/generative-ai");

require("dotenv").config();

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function analyzeCode(milestone, repoStructure, repoCode) {

    const model = genAI.getGenerativeModel({
        model: "gemini-2.5-flash"
    });

const prompt = `
You are a strict and experienced software QA engineer reviewing a GitHub repository.

Milestone Requirement:
${milestone}

Repository File Structure:
${repoStructure}

Repository Code Snippets:
${repoCode}

Evaluate milestone completion.

Guidelines:
- Analyze filenames and code.
- Check if milestone logic exists.
- Estimate completion realistically.

Rules:
Completed = 100%
Not Completed = 0%
Partial = estimate between 1-99

Return ONLY JSON:

{
"status":"Completed | Partially Completed | Not Completed",
"completion_percentage":number,
"short_explanation":"brief reason"
}
`;

const result = await model.generateContent(prompt);

const response = await result.response;

return response.text();

}

module.exports = { analyzeCode };