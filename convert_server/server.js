const express = require('express');
const { exec } = require('child_process');
const app = express();
const port = 3000;

app.get('/convert-model', (req, res) => {
  const kerasModelPath = '../current_model_dir/model.h5';
  const tfjsTargetDir = '../current_model_dir';

  const convertCommand = `tensorflowjs_converter --input_format=keras ${kerasModelPath} ${tfjsTargetDir}`;

  exec(convertCommand, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      return res.status(500).send('Conversion failed');
    }

    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
    
    res.sendStatus(200);
  });
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
