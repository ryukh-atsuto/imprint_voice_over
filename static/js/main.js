document.addEventListener('DOMContentLoaded', () => {
    const sloganText = document.getElementById('slogan-text');
    const languageSelect = document.getElementById('language-select');
    const engineSelect = document.getElementById('engine-select');
    const vibeContainer = document.getElementById('vibe-container');
    const voiceContainer = document.getElementById('voice-container');
    const barkTip = document.getElementById('bark-tip');
    const generatorForm = document.getElementById('generator-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');

    const stateEmpty = document.getElementById('output-state-empty');
    const stateLoading = document.getElementById('output-state-loading');
    const stateResult = document.getElementById('output-state-result');
    const stateError = document.getElementById('output-state-error');

    const loadingStatusText = document.getElementById('loading-status-text');
    const resultMetaText = document.getElementById('result-meta-text');
    const audioPreview = document.getElementById('audio-preview');
    const downloadBtn = document.getElementById('download-btn');
    const retryBtn = document.getElementById('retry-btn');
    const errorMessage = document.getElementById('error-message');

    // Engine mapping based on selected language
    const engineMapping = {
        'English': [
            { value: 'Bark (Expressive, Slow)', text: 'Bark (Expressive, Slow)' },
            { value: 'Kokoro (Ultra-Fast Voice + Background Music)', text: 'Kokoro (Ultra-Fast Voice + Background Music)' }
        ],
        'Bangla': [
            { value: 'Meta MMS / Indic-TTS (Native Bangla Speed)', text: 'Meta MMS / Indic-TTS (Native Bangla Speed)' }
        ]
    };

    // When language changes, update engine options
    languageSelect.addEventListener('change', () => {
        const selectedLang = languageSelect.value;
        
        // Clear previous options
        engineSelect.innerHTML = '';
        
        if (engineMapping[selectedLang]) {
            engineSelect.disabled = false;
            engineMapping[selectedLang].forEach(engine => {
                const opt = document.createElement('option');
                opt.value = engine.value;
                opt.textContent = engine.text;
                engineSelect.appendChild(opt);
            });
            // Trigger change event to set correct initial visual elements
            engineSelect.dispatchEvent(new Event('change'));
        } else {
            engineSelect.disabled = true;
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = 'Choose language first';
            engineSelect.appendChild(opt);
        }
    });

    // When engine changes, show/hide context-specific input sub-options
    engineSelect.addEventListener('change', () => {
        const selectedEngine = engineSelect.value;

        // Reset all dynamic elements
        barkTip.classList.add('hidden-element');
        vibeContainer.classList.add('hidden-element');
        voiceContainer.classList.add('hidden-element');

        if (selectedEngine.includes('Bark')) {
            barkTip.classList.remove('hidden-element');
        } else if (selectedEngine.includes('Kokoro')) {
            vibeContainer.classList.remove('hidden-element');
            voiceContainer.classList.remove('hidden-element');
        }
    });

    // Form Submission Handling
    generatorForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            text: sloganText.value.trim(),
            language: languageSelect.value,
            engine: engineSelect.value,
            background_vibe: document.getElementById('vibe-select').value,
            voice: document.getElementById('voice-select').value
        };

        if (!payload.text) return;

        // Show loading state
        submitBtn.disabled = true;
        btnText.textContent = 'Generating Audio...';
        spinner.classList.remove('hidden-element');

        showState(stateLoading);
        
        // Customize loading message
        if (payload.engine.includes('Bark')) {
            loadingStatusText.textContent = 'Bark is generating expressive speech. The first execution will download the model weights (~250MB). This may take several minutes...';
        } else if (payload.engine.includes('Kokoro')) {
            loadingStatusText.textContent = 'Generating speech with Kokoro and overlaying background music using Pydub...';
        } else if (payload.engine.includes('Meta MMS')) {
            loadingStatusText.textContent = 'Meta MMS is loading Bangla phonemization mapping and generating speech...';
        }

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok || result.error) {
                throw new Error(result.error || 'Audio synthesis failed.');
            }

            // Set up result state
            resultMetaText.textContent = `Language: ${payload.language} | Engine: ${payload.engine.split(' ')[0]}`;
            audioPreview.src = result.audio_url;
            downloadBtn.href = result.audio_url;
            downloadBtn.setAttribute('download', `${payload.language.toLowerCase()}_slogan_${result.filename}`);
            
            showState(stateResult);
            audioPreview.play().catch(err => console.log("Autoplay prevented by browser security policy"));

        } catch (err) {
            console.error("Synthesis error:", err);
            errorMessage.textContent = err.message || 'An error occurred during audio synthesis.';
            showState(stateError);
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = 'Generate Audio (MP3)';
            spinner.classList.add('hidden-element');
        }
    });

    retryBtn.addEventListener('click', () => {
        showState(stateEmpty);
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
