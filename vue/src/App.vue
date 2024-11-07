<template>
  <div>
    <el-upload
      ref="upload"
      class="upload-demo"
      action="/faster-whisper/file/upload"
      :limit="1"
      :on-exceed="handleExceed"
      :on-success="handleSuccess"
      :auto-upload="false"
    >
      <template #trigger>
        <el-button type="primary">select file</el-button>
      </template>
      <el-button class="ml-3" type="success" @click="submitUpload">
        upload to server
      </el-button>
      <template #tip>
        <div class="el-upload__tip text-red">
          Please slelect an audio file.
        </div>
      </template>
    </el-upload>
  </div>
  <div class="mb-4">
    <el-button type="primary" @click="submitTranscribe">Transcribe</el-button>
  </div>
  <div>
    <el-button type="success" @click="submitDownload">Download</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { genFileId } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile } from 'element-plus'

let localCache = {}

// upload code begin
const upload = ref<UploadInstance>()

const handleExceed: UploadProps['onExceed'] = (response, files) => {
  upload.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  upload.value!.handleStart(file)
}

// 监听文件上传成功事件
const handleSuccess: UploadProps['onSuccess'] = (response, file, fileList) => {
  console.log('File uploaded onSuccess:', response);
  localCache.uploaded_file_name = response.file_name
};

const submitUpload = () => {
  upload.value!.submit()
}
// upload code end 

// Transcribe begin
async function postTranscribe(sendData) {
  try {
    const response = await fetch('/faster-whisper/task/start', {
      method: 'POST', // 或者 'POST', 'PUT', 'DELETE' 等
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(sendData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log(data);
    localCache.subtitle_file_name = data.subtitle_file_name
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
  }
}

const submitTranscribe = () => {
  if (localCache.uploaded_file_name == null) {
    return;
  }
  let body = {
    audio_file_name: localCache.uploaded_file_name
  }
  postTranscribe(body)
}
// Transcribe end

// download begin
async function downloadFile(filename) {
  try {
    const url = `/faster-whisper/file/download/${filename}`
    const response = await fetch(url, {
      method: 'GET', // 或者 'POST', 'PUT', 'DELETE' 等
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 转换为 Blob
    const blob = await response.blob();
    // 创建 URL 对象
    const fileURL = window.URL.createObjectURL(blob);
    // 创建链接并模拟点击
    const link = document.createElement('a');
    link.href = fileURL;
    link.setAttribute('download', filename); // 指定下载文件名
    document.body.appendChild(link);
    link.click();

    // 从文档中移除链接
    document.body.removeChild(link);

    // 释放 URL 对象
    window.URL.revokeObjectURL(fileURL);
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
  }
}

const submitDownload = () => {
  if (localCache.subtitle_file_name == null) {
    return
  }
  downloadFile(localCache.subtitle_file_name)
}
// download end
</script>

<style scoped>
.ml-3 {
    margin-left: 0.75rem;
}
.mb-4 {
  margin-bottom: 1rem;
}
</style>
