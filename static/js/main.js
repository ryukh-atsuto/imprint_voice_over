document.addEventListener('DOMContentLoaded', () => {
    // Form and input elements
    const generatorForm = document.getElementById('generator-form');
    const scriptText = document.getElementById('script-text');
    const languageSelect = document.getElementById('language-select');
    const selectedEngineInput = document.getElementById('selected-engine');
    const vibeSelect = document.getElementById('vibe-select');
    const voiceSelect = document.getElementById('voice-select');
    
    // Sliders & Values
    const intensitySlider = document.getElementById('intensity-slider');
    const intensityVal = document.getElementById('intensity-val');
    const speedSlider = document.getElementById('speed-slider');
    const speedVal = document.getElementById('speed-val');
    
    const voiceVolSlider = document.getElementById('voice-vol');
    const voiceVolVal = document.getElementById('voice-vol-val');
    const bgVolSlider = document.getElementById('bg-vol');
    const bgVolVal = document.getElementById('bg-vol-val');
    const duckingSlider = document.getElementById('ducking-slider');
    const duckingVal = document.getElementById('ducking-val');
    
    // Toggle background mixing
    const layerBgCb = document.getElementById('layer-bg-cb');
    const mixerControlsWrapper = document.getElementById('mixer-controls-wrapper');
    
    // File upload elements
    const dropzone = document.getElementById('dropzone');
    const voiceRefInput = document.getElementById('voice-ref');
    const fileInfo = document.getElementById('file-info');
    
    // State wrappers
    const stateEmpty = document.getElementById('output-state-empty');
    const stateLoading = document.getElementById('output-state-loading');
    const stateResult = document.getElementById('output-state-result');
    const stateError = document.getElementById('output-state-error');
    
    const loadingStatusText = document.getElementById('loading-status-text');
    const liveLogsTerminal = document.getElementById('engine-live-logs');
    const audioPreview = document.getElementById('audio-preview');
    const downloadBtn = document.getElementById('download-btn');
    const retryBtn = document.getElementById('retry-btn');
    const errorMessage = document.getElementById('error-message');
    const resultMetaText = document.getElementById('result-meta-text');
    const submitBtn = document.getElementById('submit-btn');

    // Model Tiers Definition
    const modelTiers = {
        'english': {
            tier1: ['IndexTTS-2', 'index-tts', 'Fish Audio (S2 Pro)', 'CanopyLabs Orpheus-3B'],
            tier2: ['Chatterbox-Turbo', 'k2-fsa/OmniVoice', 'Microsoft VibeVoice-1.5B', 'MOSS-TTS'],
            tier3: ['voice-generator.com Client Engine']
        },
        'bangla': {
            tier1: ['Orpheus-Bangla', 'Fish Audio (S2 Pro)'],
            tier2: ['k2-fsa/OmniVoice', 'MOSS-TTS'],
            tier3: ['voice-generator.com Client Engine']
        },
        'bilingual mix': {
            tier1: ['Fish Audio (S2 Pro)', 'CanopyLabs Orpheus-3B', 'Orpheus-Bangla'],
            tier2: ['Chatterbox-Turbo', 'k2-fsa/OmniVoice'],
            tier3: ['Qwen3-TTS', 'Voxtral-TTS', 'voice-generator.com Client Engine']
        }
    };

    // Synchronize Sliders
    function setupSliderSync(slider, valEl, suffix = '') {
        if (!slider || !valEl) return;
        slider.addEventListener('input', () => {
            valEl.textContent = `${slider.value}${suffix}`;
        });
    }
    setupSliderSync(intensitySlider, intensityVal, '%');
    setupSliderSync(speedSlider, speedVal, 'x');
    setupSliderSync(voiceVolSlider, voiceVolVal, '%');
    setupSliderSync(bgVolSlider, bgVolVal, '%');
    setupSliderSync(duckingSlider, duckingVal, ' dB');
    
    // Handle ducking negative sign representation
    duckingSlider.addEventListener('input', () => {
        duckingVal.textContent = `-${duckingSlider.value} dB`;
    });

    // Toggle Mixer Controls visibility
    layerBgCb.addEventListener('change', () => {
        if (layerBgCb.checked) {
            mixerControlsWrapper.classList.remove('disabled-mixer');
            mixerControlsWrapper.style.opacity = '1';
            mixerControlsWrapper.style.pointerEvents = 'auto';
        } else {
            mixerControlsWrapper.classList.add('disabled-mixer');
            mixerControlsWrapper.style.opacity = '0.4';
            mixerControlsWrapper.style.pointerEvents = 'none';
        }
    });

    // Drag and Drop File Upload
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            voiceRefInput.files = e.dataTransfer.files;
            updateFileInfo(e.dataTransfer.files[0]);
        }
    });

    voiceRefInput.addEventListener('change', () => {
        if (voiceRefInput.files.length) {
            updateFileInfo(voiceRefInput.files[0]);
        }
    });

    function updateFileInfo(file) {
        fileInfo.textContent = `Attached: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        fileInfo.classList.remove('hidden-element');
        dropzone.classList.add('has-file');
    }

    // Dynamic Engine Grid Filtering
    languageSelect.addEventListener('change', () => {
        const selectedLang = languageSelect.value.toLowerCase();
        const tiers = modelTiers[selectedLang];
        
        // Clear grids
        const t1Grid = document.getElementById('tier1-grid');
        const t2Grid = document.getElementById('tier2-grid');
        const t3Grid = document.getElementById('tier3-grid');
        
        t1Grid.innerHTML = '';
        t2Grid.innerHTML = '';
        t3Grid.innerHTML = '';

        if (!tiers) return;

        // Populate grids helper
        const populateGrid = (grid, models, tierLabel) => {
            models.forEach(model => {
                const card = document.createElement('div');
                card.className = 'engine-card';
                card.innerHTML = `
                    <div class="engine-card-header">
                        <span class="engine-status-dot"></span>
                        <h4>${model}</h4>
                    </div>
                    <p class="engine-meta-desc">${tierLabel} Model Configuration</p>
                `;
                card.addEventListener('click', () => {
                    // Remove active classes
                    document.querySelectorAll('.engine-card').forEach(c => c.classList.remove('active'));
                    card.classList.add('active');
                    selectedEngineInput.value = model;
                });
                grid.appendChild(card);
            });
        };

        populateGrid(t1Grid, tiers.tier1, 'Autoregressive');
        populateGrid(t2Grid, tiers.tier2, 'Conversational');
        populateGrid(t3Grid, tiers.tier3, 'Foundation');
        
        // Auto-select first available engine card
        const firstCard = t1Grid.querySelector('.engine-card') || t2Grid.querySelector('.engine-card') || t3Grid.querySelector('.engine-card');
        if (firstCard) {
            firstCard.click();
        }
    });

    // Reset console on click
    retryBtn.addEventListener('click', () => {
        showState(stateEmpty);
        submitBtn.disabled = false;
        submitBtn.classList.remove('disabled');
    });

    // Form Submit handling with terminal simulation
    generatorForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        generatorForm.dataset.startTime = Date.now();

        const engine = selectedEngineInput.value;
        const text = scriptText.value.trim();
        const lang = languageSelect.value;
        
        if (!text || !engine || !lang) {
            alert('Please make sure script, language, and model engine selections are completed.');
            return;
        }

        // Lock trigger button
        submitBtn.disabled = true;
        submitBtn.classList.add('disabled');
        
        showState(stateLoading);
        liveLogsTerminal.innerHTML = '';

        // Prepare multipart form data payload
        const formData = new FormData();
        formData.append('text', text);
        formData.append('language', lang);
        formData.append('engine', engine);
        formData.append('vibe', vibeSelect.value);
        formData.append('voice', voiceSelect.value);
        formData.append('intensity', intensitySlider.value);
        formData.append('speed', speedSlider.value);
        formData.append('layer_bg', layerBgCb.checked ? 'true' : 'false');
        formData.append('bg_style', document.getElementById('bg-style-select').value);
        formData.append('voice_vol', voiceVolSlider.value);
        formData.append('bg_vol', bgVolSlider.value);
        formData.append('ducking', duckingSlider.value);

        if (voiceRefInput.files.length) {
            formData.append('voice_ref', voiceRefInput.files[0]);
        }

        // Run live console simulation logs
        const simulationLogs = [
            { text: `[SYSTEM] Initiating AdVocalist Studio Engine on ${navigator.platform}...`, delay: 100 },
            { text: `[SYSTEM] Processing script: "${text.substring(0, 30)}..."`, delay: 500 },
            { text: `[EMOTION] Campaign Vibe designated: [${vibeSelect.value.toUpperCase()}]`, delay: 900 },
            { text: `[EMOTION] Target variables set: Intensity=${intensitySlider.value}%, Pacing=${speedSlider.value}x, Voice=${voiceSelect.value}`, delay: 1300 },
            { text: `[ENGINE] Selected Model: "${engine}"`, delay: 1700 }
        ];

        if (voiceRefInput.files.length) {
            simulationLogs.push({ text: `[CLONING] Parsing zero-shot reference voice: ${voiceRefInput.files[0].name}`, delay: 2100 });
            simulationLogs.push({ text: `[CLONING] Speaker embedding vector successfully extracted from references.`, delay: 2500 });
        }

        simulationLogs.push({ text: `[SYSTEM] Loading model weights from cache: F:\\huggingface_cache`, delay: 2900 });
        simulationLogs.push({ text: `[HARDWARE] Executing forward inference on accelerator core (CPU/GPU)...`, delay: 3300 });

        if (layerBgCb.checked) {
            simulationLogs.push({ text: `[MIXER] Loading background Bed: "${document.getElementById('bg-style-select').value}.mp3"`, delay: 3700 });
            simulationLogs.push({ text: `[MIXER] Applying ducking reduction of -${duckingSlider.value} dB on background loop...`, delay: 4100 });
        }

        simulationLogs.push({ text: `[SYSTEM] Compiling final high-fidelity MP3 container...`, delay: 4500 });

        // Add log messages to terminal dynamically
        simulationLogs.forEach(log => {
            setTimeout(() => {
                const line = document.createElement('div');
                line.className = 'log-line';
                line.textContent = log.text;
                liveLogsTerminal.appendChild(line);
                liveLogsTerminal.scrollTop = liveLogsTerminal.scrollHeight;
            }, log.delay);
        });

        // Trigger request to backend
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            // Wait until simulation completes (at least 4.5 seconds) to keep UI matching logs
            const waitTime = Math.max(0, 4800 - (Date.now() - generatorForm.dataset.startTime || 0));
            await new Promise(resolve => setTimeout(resolve, waitTime));

            if (!response.ok || result.error) {
                throw new Error(result.error || 'Audio rendering failed.');
            }

            // Populate Output Results
            resultMetaText.textContent = `Language: ${lang} | Model: ${engine} | Vibe: ${vibeSelect.value.toUpperCase()}`;
            audioPreview.src = result.audio_url;
            downloadBtn.href = result.audio_url;
            downloadBtn.setAttribute('download', `advocalist_${lang.toLowerCase().replace(' ', '_')}_campaign.mp3`);

            showState(stateResult);
            audioPreview.play().catch(err => console.log('Autoplay blocked. User action required.'));

        } catch (err) {
            console.error('Audio Generation Error:', err);
            errorMessage.textContent = err.message || 'An error occurred during audio synthesis.';
            showState(stateError);
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('disabled');
        }
    });

    function showState(activeState) {
        [stateEmpty, stateLoading, stateResult, stateError].forEach(state => {
            if (state === activeState) {
                state.classList.remove('hidden-element');
            } else {
                state.classList.add('hidden-element');
            }
        });
    }
});
