const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("financial_statement");
const fileList = document.getElementById("fileList");
const dt = new DataTransfer();

const addFiles = files => {
  const currentCount = dt.files.length;
  const newFiles = Array.from(files);

  if (currentCount + newFiles.length > 4) {
    alert("You can upload up to 4 files only.");
    // Optionally add only files that fit in the limit
    const allowedFiles = newFiles.slice(0, 4 - currentCount);
    for (const file of allowedFiles) {
      if (![...dt.files].some(f => f.name === file.name && f.size === file.size)) {
        dt.items.add(file);
      }
    }
  } else {
    for (const file of newFiles) {
      if (![...dt.files].some(f => f.name === file.name && f.size === file.size)) {
        dt.items.add(file);
      }
    }
  }

  fileInput.files = dt.files;
  renderFiles();
};

const renderFiles = () => {
  fileList.innerHTML = "";
  [...dt.files].forEach((file, i) => {
    const div = document.createElement("div");
    div.textContent = file.name;
    const btn = Object.assign(document.createElement("button"), {
      textContent: "×",
      title: "Remove this file",
      style: "margin-left:10px; cursor:pointer; border:none; background:transparent; color:red; font-weight:bold;"
    });
    btn.onclick = () => {
      dt.items.remove(i);
      fileInput.files = dt.files;
      renderFiles();
    };
    div.appendChild(btn);
    fileList.appendChild(div);
  });
};

dropZone.onclick = () => fileInput.click();
dropZone.ondragover = e => { e.preventDefault(); dropZone.classList.add("dragover"); };
dropZone.ondragleave = () => dropZone.classList.remove("dragover");
dropZone.ondrop = e => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
};
fileInput.onchange = () => addFiles(fileInput.files);
