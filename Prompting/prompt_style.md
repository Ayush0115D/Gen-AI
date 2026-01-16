# Prompt styles
## 1.Alpaca prompt template
### Instructions <system_prompt>\n
### Input <user_query>
### Response: \n
### Example-
messages = [

   {"role": "system", "content": SYSTEM_PROMPT},

  {"role": "user", "content": "write a code to add n numbers in js"},

 ]
### Alpaca style
 Instruction: Write a JavaScript program to add n numbers.

Input: None

Response:
## 2.Chat ML
{
    role:"system"|"user"|"assistant"
    content:"string"
}
### It is used by openai,gemini
## Inst Prompting
### (used by llama2)
[INST] WHAT IS TIME NOW? [/INST]
It keep content inside braces
