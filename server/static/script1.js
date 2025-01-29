const output = document.getElementById("output");
const commandInput = document.getElementById("command-input");

const commands = {
  help: "Available commands: help, echo, clear, date, _dashboard",
  echo: (args) => args.join(" "),
  clear: () => { output.innerHTML = ""; return ""; },
  date: () => new Date().toString(),
  _dashboard: () => {window.location.href = `${window.location.origin}/dashboard`}
};

async function executeCommand(input) {
  const parts = input.trim().split(" ");
  const cmd = parts[0];
  const args = parts.slice(1);

  if (commands[cmd]) {
    return typeof commands[cmd] === "function" ? commands[cmd](args) : commands[cmd];
  } else {
    try {
      const response = await fetch(`${window.location.origin}/execute_command`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd, args, id }),
      });
      if (response.ok) {
        const data = await response.json();
        return data.result || `${JSON.parse(JSON.stringify(data).replace('\n','<br>'))}`;/* https://stackoverflow.com/questions/21942418/javascript-recursive-replace-in-object */
      } else {
        return `API Error: ${response.status} ${response.statusText}`;
      }
    } catch (error) {
      return `Error connecting to API: ${error.message}`;
    }
  }
}

commandInput.addEventListener("keydown", async (e) => {
  if (e.key === "Enter") {
    const input = commandInput.value.trim();
    if (input) {
      output.innerHTML += `> ${input}\n`;
      const result = await executeCommand(input);
      if (result) output.innerHTML += `${result}\n`;
      commandInput.value = "";
      output.scrollTop = output.scrollHeight;
    }
  }
});