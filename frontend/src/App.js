import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [novelFile, setNovelFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [sceneText, setSceneText] = useState('');
  const [choices, setChoices] = useState([]);
  const [voiceText, setVoiceText] = useState('');
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [saves, setSaves] = useState([]);

  useEffect(() => {
    loadSaves();
  }, []);

  const loadSaves = async () => {
    try {
      const resp = await axios.get(`${API_BASE}/saves`);
    } catch (e) {
      console.warn('Could not load saves', e);
    }
  };

  const handleNovelChange = (e) => {
    const file = e.target.files[0];
    setNovelFile(file);
  };

  const uploadNovel = async () => {
    if (!novelFile) return;
    setUploadStatus('Uploading...');
    const form = new FormData();
    form.append('file', novelFile);
    try {
      const resp = await axios.post(`${API_BASE}/novel/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus(`Uploaded: ${resp.data.message}`);
      setSessionId(`session_${Date.now()}`);
      await extractEntities();
    } catch (err) {
      setUploadStatus('Upload failed');
      console.error(err);
    }
  };

  const extractEntities = async () => {
    if (!novelFile) return;
    try {
      const form = new FormData();
      form.append('novel_filename', novelFile.name);
      const resp = await axios.post(`${API_BASE}/entity/extract`, form);
      console.log('Entities extracted:', resp.data);
    } catch (e) {
      console.error('Entity extraction failed', e);
    }
  };

  const handleChoice = async (choice) => {
    if (!sessionId) return;
    try {
      const resp = await axios.post(`${API_BASE}/scene/generate`, {
        session_id: sessionId,
        action: choice
      });
      setSceneText(resp.data.scene_text);
      setChoices(resp.data.choices);
    } catch (e) {
      console.error('Scene generation failed', e);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const form = new FormData();
        form.append('file', blob, 'audio.wav');
        try {
          const resp = await axios.post(`${API_BASE}/voice/transcribe`, form, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          setVoiceText(resp.data.text);
          if (sessionId) {
            const resp2 = await axios.post(`${API_BASE}/scene/generate`, {
              session_id: sessionId,
              action: resp.data.text
            });
            setSceneText(resp2.data.scene_text);
            setChoices(resp2.data.choices);
          }
        } catch (e) {
          console.error('Voice transcription failed', e);
        }
        setRecording(false);
      };
      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (err) {
      console.error('Microphone access error', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  };

  const saveGame = async () => {
    if (!sessionId) return;
    const saveName = prompt('Enter save name:', `save_${Date.now()}`);
    if (!saveName) return;
    try {
      const resp = await axios.post(`${API_BASE}/save/game`, {
        session_id: sessionId,
        save_name: saveName
      });
      alert(resp.data.message);
      loadSaves();
    } catch (e) {
      console.error('Save failed', e);
      alert('Save failed');
    }
  };

  const loadGame = async (saveName) => {
    try {
      const resp = await axios.post(`${API_BASE}/load/game`, { save_name: saveName });
      alert('Game loaded: ' + JSON.stringify(resp.data));
    } catch (e) {
      console.error('Load failed', e);
      alert('Load failed');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Interactive Storyline Agent</h1>
        <p className="text-sm text-gray-600">Upload a novel and embark on an interactive journey.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <aside className="lg:col-span-1 bg-white p-4 rounded-lg shadow">
          <section>
            <h2 className="font-semibold mb-2">Novel Upload</h2>
            <input
              type="file"
              accept=".pdf,.epub,.txt"
              onChange={handleNovelChange}
              className="mb-2 w-full"
            />
            <button
              onClick={uploadNovel}
              disabled={!novelFile}
              className="w-full bg-blue-600 text-white py-2 rounded mb-4"
            >
              Upload Novel
            </button>
            <p className="text-xs text-gray-500">{uploadStatus}</p>
          </section>

          <section className="mt-6">
            <h2 className="font-semibold mb-2">Voice Input</h2>
            <button
              onClick={recording ? stopRecording : startRecording}
              disabled={!sessionId}
              className={`w-full ${recording ? 'bg-red-500' : 'bg-green-600'} text-white py-2 rounded`}
            >
              {recording ? 'Stop Recording' : 'Record Voice'}
            </button>
            {voiceText && (
              <div className="mt-2 p-2 bg-gray-100 rounded">
                <strong>Transcribed:</strong> {voiceText}
              </div>
            )}
          </section>

          <section className="mt-6">
            <h2 className="font-semibold mb-2">Save / Load</h2>
            <button
              onClick={saveGame}
              disabled={!sessionId}
              className="w-full bg-indigo-600 text-white py-2 rounded mb-2"
            >
              Save Game
            </button>
            <div>
              <button onClick={() => loadGame('latest_save')} className="w-full text-left text-sm text-blue-600">
                Load Latest Save
              </button>
            </div>
          </section>
        </aside>

        <main className="lg:col-span-2 bg-white p-6 rounded-lg shadow">
          <div id="story" className="mb-6 min-h-96 whitespace-pre-line text-lg">
            {sceneText || 'Upload a novel to begin...'}
          </div>
          {choices.length > 0 && (
            <div className="space-y-3">
              <span className="font-semibold">What do you do?</span>
              {choices.map((choice, idx) => (
                <button
                  key={idx}
                  onClick={() => handleChoice(choice)}
                  className="w-full text-left bg-gray-200 py-3 rounded hover:bg-gray-300 transition"
                >
                  {choice}
                >
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
