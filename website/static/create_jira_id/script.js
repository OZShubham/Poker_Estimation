function handleFileSelect(event) {
    event.preventDefault();
    var files = event.dataTransfer ? event.dataTransfer.files : event.target.files;

    // Process the file here
    // You can access the file using 'files[0]' and perform necessary operations
    // For example, you can display the file name:
    document.getElementById('file').textContent = files[0].name;
  }

  function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
  }