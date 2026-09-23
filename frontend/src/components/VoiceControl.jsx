import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Mic, 
  MicOff, 
  Send, 
  Volume2, 
  VolumeX, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Moon, 
  Film, 
  Home as HomeIcon, 
  Bot, 
  User, 
  Lightbulb, 
  Lock, 
  ThermometerSnowflake,
  Globe,
  ArrowRight,
  Radio,
  Zap,
  Square,
  HelpCircle
} from 'lucide-react';
import { sendVoiceCommand, getTtsAudioUrl } from '../services/api';
import { formatDeviceName } from '../utils/deviceUtils';

const LANGUAGES = [
  { code: 'te-IN', label: 'తెలుగు (Telugu)', flag: '🇮🇳', short: 'TE', langKey: 'te' },
  { code: 'hi-IN', label: 'हिन्दी (Hindi)', flag: '🇮🇳', short: 'HI', langKey: 'hi' },
  { code: 'en-US', label: 'English (US)', flag: '🇺🇸', short: 'EN-US', langKey: 'en' },
  { code: 'en-IN', label: 'English (India)', flag: '🇮🇳', short: 'EN-IN', langKey: 'en' },
  { code: 'es-ES', label: 'Español (Spanish)', flag: '🇪🇸', short: 'ES', langKey: 'es' },
  { code: 'fr-FR', label: 'Français (French)', flag: '🇫🇷', short: 'FR', langKey: 'fr' },
];

const WAKE_WORD_PRESETS = [
  { 
    id: 'any', 
    label: 'Any Wake Word (Most Flexible)', 
    triggers: [
      'hey jarvis', 'jarvis', 'జార్విస్', 'జావిస్', 'जार्विस', 
      'hey smart home', 'smart home', 'స్మార్ట్ హోమ్', 'स्मार्ट होम', 
      'హలో', 'నమస్కారం', 'namaste', 'नमस्ते', 'सुनो', 'hello',
      'alexa', 'computer', 'అలెక్సా'
    ] 
  },
  { 
    id: 'jarvis', 
    label: 'Hey Jarvis / Jarvis', 
    triggers: ['hey jarvis', 'jarvis', 'జార్విస్', 'జావిస్', 'जार्विस', 'हाय जार्विस', 'హే జార్విస్'] 
  },
  { 
    id: 'smarthome', 
    label: 'Smart Home / స్మార్ట్ హోమ్', 
    triggers: ['hey smart home', 'smart home', 'స్మార్ట్ హోమ్', 'स्मार्ट होम', 'హే స్మార్ట్ హోమ్'] 
  },
  { 
    id: 'regional', 
    label: 'హలో (Hello - Telugu) / नमस्ते (Hindi)', 
    triggers: ['హలో', 'నమస్కారం', 'namaste', 'नमस्ते', 'सुनो', 'చెప్పు', 'hello'] 
  }
];

const MULTILINGUAL_COMMANDS = {
  'te': [
    { label: 'అన్ని లైట్లు ఆఫ్ చేయి', icon: Lightbulb, query: 'అన్ని లైట్లు ఆఫ్ చేయి' },
    { label: 'శుభరాత్రి', icon: Moon, query: 'శుభరాత్రి' },
    { label: 'డోర్ లాక్ చేయి', icon: Lock, query: 'డోర్ లాక్ చేయి' },
    { label: 'ఏసీ ఆన్ చేయి', icon: ThermometerSnowflake, query: 'ఏసీ ఆన్ చేయి' },
    { label: 'ఏమి ఆన్ లో ఉంది?', icon: Sparkles, query: 'ఏమి ఆన్ లో ఉంది?' },
    { label: 'లివింగ్ రూమ్ లైట్ ఆన్', icon: Lightbulb, query: 'లివింగ్ రూమ్ లైట్ ఆన్ చేయి' },
    { label: 'సినిమా మోడ్', icon: Film, query: 'సినిమా మోడ్' },
  ],
  'hi': [
    { label: 'सब लाइटें बंद करो', icon: Lightbulb, query: 'सब लाइटें बंद करो' },
    { label: 'शुभ रात्रि', icon: Moon, query: 'शुभ रात्रि' },
    { label: 'दरवाजा लॉक करो', icon: Lock, query: 'दरवाजा लॉक करो' },
    { label: 'एसी चालू करो', icon: ThermometerSnowflake, query: 'एसी चालू करो' },
    { label: 'क्या चालू है?', icon: Sparkles, query: 'क्या चालू है?' },
    { label: 'लिविंग रूम लाइट चालू', icon: Lightbulb, query: 'लिविंग रूम की लाइट चालू करो' },
    { label: 'पार्टी मोड', icon: Sparkles, query: 'पार्टी मोड' },
  ],
  'en': [
    { label: 'Turn off all lights', icon: Lightbulb, query: 'Turn off all lights' },
    { label: 'Good night routine', icon: Moon, query: 'Good night' },
    { label: 'Lock front door', icon: Lock, query: 'Lock the front door' },
    { label: 'Turn on AC', icon: ThermometerSnowflake, query: 'Turn on the AC' },
    { label: 'What is on?', icon: Sparkles, query: 'What devices are on?' },
    { label: 'Movie night mode', icon: Film, query: 'Movie mode' },
    { label: 'Welcome home', icon: HomeIcon, query: 'Welcome home' },
  ],
  'es': [
    { label: 'Apaga todas las luces', icon: Lightbulb, query: 'Apaga todas las luces' },
    { label: 'Buenas noches', icon: Moon, query: 'Buenas noches' },
    { label: 'Cierra la puerta', icon: Lock, query: 'Cierra la puerta' },
    { label: 'Enciende el aire', icon: ThermometerSnowflake, query: 'Enciende el aire acondicionado' },
    { label: '¿Qué está encendido?', icon: Sparkles, query: '¿Qué dispositivos están encendidos?' },
    { label: 'Modo película', icon: Film, query: 'Modo película' },
  ],
  'fr': [
    { label: 'Éteins toutes les lumières', icon: Lightbulb, query: 'Éteins toutes les lumières' },
    { label: 'Bonne nuit', icon: Moon, query: 'Bonne nuit' },
    { label: 'Verrouille la porte', icon: Lock, query: 'Verrouille la porte' },
    { label: 'Allume la clim', icon: ThermometerSnowflake, query: 'Allume la climatisation' },
    { label: "Qu'est-ce qui est allumé ?", icon: Sparkles, query: "Qu'est-ce qui est allumé ?" },
    { label: 'Mode cinéma', icon: Film, query: 'Mode cinéma' },
  ]
};

const WELCOME_MESSAGES = {
  'te': "నమస్కారం! నేను మీ బహుభాషా AI అసిస్టెంట్‌ని. లైట్లు, ఏసీ, ఫ్యాన్, డోర్ లేదా సీన్లు నియంత్రించడానికి మాట్లాడండి.",
  'hi': "नमस्ते! मैं आपका बहुभाषी AI सहायक हूँ। लाइटें, पंखा, एसी, दरवाजा या स्मार्ट सीन नियंत्रित करने के लिए बोलें।",
  'en': "Hello! I'm your Multilingual AI Assistant. Speak or type to control devices, scenes, or query status.",
  'es': "¡Hola! Soy tu asistente de hogar multilingüe. Habla o escribe para controlar luces, puertas y clima.",
  'fr': "Bonjour ! Je suis votre assistant maison multilingue. Parlez ou tapez pour contrôler vos lumières et clim."
};

const WAKE_WORD_ACK = {
  'te': "చెప్పండి, నేను వింటున్నాను!",
  'hi': "जी, मैं सुन रहा हूँ, बताइए!",
  'en': "Yes, I am listening!",
  'es': "¡Sí, te escucho!",
  'fr': "Oui, je vous écoute !"
};

const LANG_NAME_MAP = {
  'te': 'తెలుగు',
  'hi': 'हिन्दी',
  'en': 'English',
  'es': 'Español',
  'fr': 'Français',
};

const LOCALE_MAP = {
  'te': 'te-IN',
  'hi': 'hi-IN',
  'en': 'en-US',
  'es': 'es-ES',
  'fr': 'fr-FR'
};

export default function VoiceControl({ devices, onStateUpdate }) {
  // Stored language selection
  const [selectedLang, setSelectedLang] = useState(() => {
    return localStorage.getItem('ai_smart_home_lang') || 'te-IN';
  });

  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [transcriptPreview, setTranscriptPreview] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);

  // Hands-Free Wake Word States
  const [wakeWordEnabled, setWakeWordEnabled] = useState(() => {
    return localStorage.getItem('ai_smart_home_wakeword') === 'true';
  });
  const [selectedWakePresetId, setSelectedWakePresetId] = useState('any');
  
  // 'IDLE' | 'AWAKE' (active command listening after wake word detected)
  const [wakeStage, setWakeStage] = useState('IDLE');
  const [lastWakeWordHeard, setLastWakeWordHeard] = useState('');

  const currentLangKey = selectedLang.split('-')[0];

  // Conversation messages state
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: WELCOME_MESSAGES[currentLangKey] || WELCOME_MESSAGES['te'],
      language: currentLangKey,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      actions: []
    }
  ]);

  // Refs to prevent closure staleness and duplicate browser instances
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const isListeningRef = useRef(false);
  const isExecutingRef = useRef(false);
  const isSpeakingRef = useRef(false);
  const isProcessingRef = useRef(false);
  const wakeWordEnabledRef = useRef(wakeWordEnabled);
  const shouldRestartRef = useRef(false);
  const restartTimerRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const awakeTimeoutRef = useRef(null);
  const finalTranscriptRef = useRef('');
  const audioPlayerRef = useRef(null);
  const availableVoicesRef = useRef([]);

  // Check Web Speech API support
  const SpeechRecognition = typeof window !== 'undefined' && (
    window.SpeechRecognition || window.webkitSpeechRecognition
  );
  const hasSpeechSupport = !!SpeechRecognition;

  useEffect(() => {
    wakeWordEnabledRef.current = wakeWordEnabled;
    shouldRestartRef.current = wakeWordEnabled;
    localStorage.setItem('ai_smart_home_wakeword', wakeWordEnabled ? 'true' : 'false');
  }, [wakeWordEnabled]);

  useEffect(() => {
    isSpeakingRef.current = isSpeaking;
  }, [isSpeaking]);

  useEffect(() => {
    isProcessingRef.current = isProcessing;
  }, [isProcessing]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, transcriptPreview]);

  // Cache browser voices for fallback
  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const loadVoices = () => {
        availableVoicesRef.current = window.speechSynthesis.getVoices() || [];
      };
      loadVoices();
      window.speechSynthesis.onvoiceschanged = loadVoices;
      return () => {
        window.speechSynthesis.onvoiceschanged = null;
      };
    }
  }, []);

  // On initial mount: if wakeWord was enabled in localStorage, start listening
  useEffect(() => {
    if (wakeWordEnabled && hasSpeechSupport) {
      const timer = setTimeout(() => {
        startRecognition();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, []);

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      clearSilenceTimer();
      clearAwakeTimeout();
      stopAudioPlayback();
      stopRecognition(false);
    };
  }, []);

  const clearSilenceTimer = () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  };

  const clearAwakeTimeout = () => {
    if (awakeTimeoutRef.current) {
      clearTimeout(awakeTimeoutRef.current);
      awakeTimeoutRef.current = null;
    }
  };

  // Zero-latency pleasant ding chime when wake word activates
  const playWakeChime = useCallback(() => {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch (_) {}
  }, []);

  // Stop audio playback
  const stopAudioPlayback = () => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  // Browser SpeechSynthesis fallback
  const playBrowserSynthesisFallback = (text, langCode) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setIsSpeaking(false);
      return;
    }
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      const targetLocale = LOCALE_MAP[langCode] || selectedLang;
      utterance.lang = targetLocale;

      const voices = availableVoicesRef.current || [];
      const prefix = (langCode || 'en').toLowerCase();
      const matched = voices.find(v => v.lang.toLowerCase() === targetLocale.toLowerCase()) ||
                      voices.find(v => v.lang.toLowerCase().startsWith(prefix));
      if (matched) utterance.voice = matched;

      utterance.onend = () => {
        setIsSpeaking(false);
        resumeAfterSpeaking();
      };
      utterance.onerror = () => {
        setIsSpeaking(false);
        resumeAfterSpeaking();
      };

      window.speechSynthesis.speak(utterance);
    } catch (_) {
      setIsSpeaking(false);
    }
  };

  // Resume listening after speaking finishes
  const resumeAfterSpeaking = () => {
    if (wakeWordEnabledRef.current && !isListeningRef.current) {
      setTimeout(() => {
        startRecognition();
      }, 400);
    }
  };

  // Speak response out loud in authentic native language via FastAPI gTTS streaming
  const speakResponse = async (text, responseLang) => {
    if (!ttsEnabled || !text) return;

    stopAudioPlayback();
    setIsSpeaking(true);

    const cleanLang = (responseLang || currentLangKey || 'te').split('-')[0].toLowerCase();

    // Pause recognition while speaking so assistant audio does not self-trigger
    stopRecognition(false);

    try {
      const audioUrl = getTtsAudioUrl(text, cleanLang);
      const audio = new Audio(audioUrl);
      audioPlayerRef.current = audio;

      audio.onended = () => {
        setIsSpeaking(false);
        audioPlayerRef.current = null;
        resumeAfterSpeaking();
      };

      audio.onerror = () => {
        playBrowserSynthesisFallback(text, cleanLang);
      };

      await audio.play();
    } catch (err) {
      console.warn('Streaming TTS error, falling back to browser synthesis:', err);
      playBrowserSynthesisFallback(text, cleanLang);
    }
  };

  // Handle language switch
  const handleLanguageChange = (langCode) => {
    setSelectedLang(langCode);
    localStorage.setItem('ai_smart_home_lang', langCode);
    const key = langCode.split('-')[0];
    const welcomeText = WELCOME_MESSAGES[key] || WELCOME_MESSAGES['te'];
    
    setMessages(prev => [
      ...prev,
      {
        id: Date.now(),
        sender: 'assistant',
        text: welcomeText,
        language: key,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        actions: []
      }
    ]);

    if (ttsEnabled) {
      speakResponse(welcomeText, key);
    }

    // Restart recognition with the newly selected language acoustic model
    if (wakeWordEnabledRef.current || isListeningRef.current) {
      stopRecognition(false);
      setTimeout(() => {
        startRecognition();
      }, 350);
    }
  };

  // Stop recognition completely and safely
  const stopRecognition = (restartLater = false) => {
    shouldRestartRef.current = restartLater && wakeWordEnabledRef.current;
    
    if (restartTimerRef.current) {
      clearTimeout(restartTimerRef.current);
      restartTimerRef.current = null;
    }
    
    clearSilenceTimer();

    if (recognitionRef.current) {
      try {
        recognitionRef.current.onend = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onresult = null;
        recognitionRef.current.abort();
      } catch (_) {}
      recognitionRef.current = null;
    }

    isListeningRef.current = false;
    setIsListening(false);
  };

  // Safe, single-instance speech recognition start
  const startRecognition = () => {
    if (!hasSpeechSupport) {
      setErrorMessage("Speech recognition is not supported in this browser. Please type your command below.");
      return;
    }

    if (isSpeakingRef.current) {
      return; // Do not listen while speaking to prevent feedback loops
    }

    // Stop existing instance cleanly before launching a new one
    stopRecognition(false);

    setErrorMessage(null);
    clearSilenceTimer();
    finalTranscriptRef.current = '';
    isExecutingRef.current = false;
    shouldRestartRef.current = wakeWordEnabledRef.current;

    try {
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = selectedLang; // Native acoustic model (te-IN, hi-IN, en-US, etc.)

      rec.onstart = () => {
        isListeningRef.current = true;
        setIsListening(true);
      };

      rec.onresult = (event) => {
        let interim = '';
        let finalPiece = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalPiece += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        if (finalPiece) {
          finalTranscriptRef.current += (finalTranscriptRef.current ? ' ' : '') + finalPiece.trim();
        }

        const fullCaptured = (finalTranscriptRef.current + (interim ? ' ' + interim : '')).trim();
        setTranscriptPreview(fullCaptured);

        if (!fullCaptured) return;

        // ==========================================
        // STAGE 2: AWAKE STAGE (Wake word already heard, now speaking command!)
        // ==========================================
        if (wakeWordEnabledRef.current && wakeStage === 'AWAKE') {
          clearSilenceTimer();
          // User is speaking their command: wait for 1.1s silence to execute
          silenceTimerRef.current = setTimeout(() => {
            if (!isExecutingRef.current && fullCaptured) {
              isExecutingRef.current = true;
              clearAwakeTimeout();
              setWakeStage('IDLE');
              finalTranscriptRef.current = '';
              setTranscriptPreview('');
              executeCommand(fullCaptured);
            }
          }, 1100);
          return;
        }

        // ==========================================
        // STAGE 1: IDLE WAKE-WORD SEARCH
        // ==========================================
        if (wakeWordEnabledRef.current && wakeStage === 'IDLE') {
          const lower = fullCaptured.toLowerCase();
          const activePreset = WAKE_WORD_PRESETS.find(p => p.id === selectedWakePresetId) || WAKE_WORD_PRESETS[0];
          const triggers = activePreset.triggers;

          let matchedTrigger = null;
          let commandAfterWake = '';

          for (const trig of triggers) {
            const trigLower = trig.toLowerCase();
            const idx = lower.indexOf(trigLower);
            if (idx !== -1) {
              matchedTrigger = trig;
              commandAfterWake = fullCaptured.slice(idx + trig.length).replace(/^[,\s.!:?-]+/, '').trim();
              break;
            }
          }

          if (matchedTrigger) {
            setLastWakeWordHeard(matchedTrigger);
            playWakeChime();

            clearSilenceTimer();
            // Wait for 1.1s silence so user can finish their complete sentence
            silenceTimerRef.current = setTimeout(() => {
              if (isExecutingRef.current) return;

              // Re-check captured text after user paused
              const latestCaptured = (finalTranscriptRef.current + (interim ? ' ' + interim : '')).trim();
              const latestLower = latestCaptured.toLowerCase();
              const latestIdx = latestLower.indexOf(matchedTrigger.toLowerCase());
              const finalCommand = latestIdx !== -1 
                ? latestCaptured.slice(latestIdx + matchedTrigger.length).replace(/^[,\s.!:?-]+/, '').trim()
                : commandAfterWake;

              if (finalCommand) {
                // CASE A: User said Wake Word + Command together (e.g. "Hey Jarvis turn on the AC")
                isExecutingRef.current = true;
                finalTranscriptRef.current = '';
                setTranscriptPreview('');
                executeCommand(finalCommand);
              } else {
                // CASE B: User said ONLY the Wake Word (e.g. "Hey Jarvis" or "హలో")
                // Acknowledge aloud and transition to 'AWAKE' stage!
                finalTranscriptRef.current = '';
                setTranscriptPreview('');
                setWakeStage('AWAKE');

                const ackText = WAKE_WORD_ACK[currentLangKey] || WAKE_WORD_ACK['te'];
                speakResponse(ackText, currentLangKey);

                // Set 8-second expiry for follow-up command
                clearAwakeTimeout();
                awakeTimeoutRef.current = setTimeout(() => {
                  setWakeStage('IDLE');
                  setLastWakeWordHeard('');
                }, 8000);
              }
            }, 1100);

            return;
          }
        }

        // ==========================================
        // MANUAL PUSH-TO-TALK MODE (Hands-free is OFF)
        // ==========================================
        if (!wakeWordEnabledRef.current && fullCaptured) {
          clearSilenceTimer();
          silenceTimerRef.current = setTimeout(() => {
            if (!isExecutingRef.current && fullCaptured) {
              isExecutingRef.current = true;
              finalTranscriptRef.current = '';
              setTranscriptPreview('');
              executeCommand(fullCaptured);
            }
          }, 1200);
        }
      };

      rec.onerror = (event) => {
        clearSilenceTimer();
        if (event.error === 'not-allowed') {
          setErrorMessage("Microphone access was denied. Please allow microphone permissions in browser settings.");
          stopRecognition(false);
          setWakeWordEnabled(false);
        } else if (event.error !== 'no-speech' && event.error !== 'aborted') {
          console.warn('Speech recognition warning:', event.error);
        }
      };

      rec.onend = () => {
        isListeningRef.current = false;
        setIsListening(false);

        // Seamless hands-free restart
        if (shouldRestartRef.current && !isSpeakingRef.current && !isProcessingRef.current) {
          restartTimerRef.current = setTimeout(() => {
            startRecognition();
          }, 350);
        }
      };

      recognitionRef.current = rec;
      rec.start();
    } catch (err) {
      console.warn('Failed to start speech recognition:', err);
      isListeningRef.current = false;
      setIsListening(false);
    }
  };

  // Toggle Hands-Free Wake Word Mode
  const toggleWakeWord = () => {
    const next = !wakeWordEnabled;
    setWakeWordEnabled(next);
    wakeWordEnabledRef.current = next;
    shouldRestartRef.current = next;
    setWakeStage('IDLE');
    setLastWakeWordHeard('');
    clearAwakeTimeout();

    if (next) {
      startRecognition();
    } else {
      stopRecognition(false);
    }
  };

  // Manual Push-to-Talk Toggle (When clicking the mic orb)
  const handleOrbClick = () => {
    if (isSpeaking) {
      stopAudioPlayback();
      return;
    }

    if (isListening) {
      // User tapped to stop and send immediately
      clearSilenceTimer();
      const textToSend = finalTranscriptRef.current.trim() || transcriptPreview.trim();
      stopRecognition(wakeWordEnabledRef.current);
      if (textToSend) {
        executeCommand(textToSend);
      }
    } else {
      // User tapped to start speaking
      startRecognition();
    }
  };

  // Execute Command (Speech, typed text, or chip click)
  const executeCommand = async (commandText) => {
    clearSilenceTimer();
    clearAwakeTimeout();
    setWakeStage('IDLE');
    setLastWakeWordHeard('');

    const textToSubmit = commandText || inputText;
    if (!textToSubmit || !textToSubmit.trim() || isProcessing) return;

    const trimmed = textToSubmit.trim();
    setInputText('');
    setTranscriptPreview('');
    setErrorMessage(null);
    finalTranscriptRef.current = '';

    // Append User Message
    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      const result = await sendVoiceCommand(trimmed, selectedLang);

      // Append Assistant Message
      const assistantMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: result.response,
        intent: result.intent,
        language: result.language || currentLangKey,
        actions: result.actions || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Speak Response in authentic native language
      speakResponse(result.response, result.language || currentLangKey);

      // Trigger dashboard state refresh
      if (onStateUpdate && result.actions && result.actions.length > 0) {
        await onStateUpdate();
      }
    } catch (err) {
      console.error('Command Execution Error:', err);
      const failMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: `Sorry, I encountered an error: ${err.message || 'Unable to execute command.'}`,
        isError: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, failMessage]);
    } finally {
      setIsProcessing(false);
      isExecutingRef.current = false;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      executeCommand();
    }
  };

  const quickCommands = MULTILINGUAL_COMMANDS[currentLangKey] || MULTILINGUAL_COMMANDS['te'];
  const activePreset = WAKE_WORD_PRESETS.find(p => p.id === selectedWakePresetId) || WAKE_WORD_PRESETS[0];

  return (
    <div className="voice-assistant-container">
      {/* Top Header Bar */}
      <div className="voice-header glass">
        <div className="voice-header-info">
          <div className="voice-title-wrapper">
            <div className="voice-ai-badge">
              <Sparkles size={16} className="sparkle-icon" />
              <span>Multilingual AI Voice Assistant</span>
            </div>
            <span className="voice-engine-tag">Powered by Gemini 3.6 Flash & Native TTS</span>
          </div>
          <p className="voice-header-desc">
            Hands-free smart home control. Speak in <strong>Telugu, Hindi, English, Spanish, or French</strong>.
          </p>
        </div>

        {/* Action Controls Bar */}
        <div className="voice-controls-bar">
          {/* Spoken Voice Preview Button */}
          <button
            className="preview-voice-btn"
            onClick={() => {
              const text = WELCOME_MESSAGES[currentLangKey] || WELCOME_MESSAGES['te'];
              speakResponse(text, currentLangKey);
            }}
            title="Hear authentic voice audio in this language"
          >
            <Volume2 size={14} />
            <span>Hear Voice</span>
          </button>

          {/* Stop Audio Button (Visible when speaking) */}
          {isSpeaking && (
            <button
              className="stop-audio-btn pulse-glow"
              onClick={stopAudioPlayback}
              title="Stop speaking audio"
            >
              <Square size={13} />
              <span>Stop Speaking</span>
            </button>
          )}

          {/* TTS Audio Mute Toggle */}
          <button 
            className={`tts-toggle-btn ${ttsEnabled ? 'active' : ''}`}
            onClick={() => {
              if (ttsEnabled) stopAudioPlayback();
              setTtsEnabled(!ttsEnabled);
            }}
            title={ttsEnabled ? "Mute spoken audio response" : "Enable voice audio response"}
          >
            {ttsEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
            <span>{ttsEnabled ? 'Audio On' : 'Muted'}</span>
          </button>
        </div>
      </div>

      {/* Prominent Spoken Language Selection Bar */}
      <div className="language-selector-section glass">
        <div className="lang-section-label">
          <Globe size={15} />
          <span>Select Spoken Language:</span>
        </div>
        <div className="lang-pill-buttons">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              className={`lang-pill-btn ${selectedLang === lang.code ? 'selected' : ''}`}
              onClick={() => handleLanguageChange(lang.code)}
              disabled={isProcessing}
            >
              <span className="lang-flag">{lang.flag}</span>
              <span className="lang-name">{lang.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Hands-Free Wake Word Card */}
      <div className={`wake-word-card glass ${wakeWordEnabled ? 'enabled' : ''} ${wakeStage === 'AWAKE' ? 'triggered' : ''}`}>
        <div className="wake-word-left">
          <div className="wake-icon-badge">
            <Radio size={16} className={wakeWordEnabled ? "wake-radio-active" : ""} />
          </div>
          <div className="wake-word-meta">
            <div className="wake-word-title-row">
              <span className="wake-word-title">Hands-Free Wake Word</span>
              {wakeWordEnabled && (
                <span className={`wake-status-badge ${wakeStage === 'AWAKE' ? 'active-awake' : ''}`}>
                  {wakeStage === 'AWAKE' 
                    ? '⚡ WAKE WORD RECOGNIZED! SPEAK COMMAND NOW...' 
                    : '● LISTENING FOR WAKE WORD'}
                </span>
              )}
            </div>
            <p className="wake-word-subtitle">
              {wakeWordEnabled 
                ? wakeStage === 'AWAKE'
                  ? `Assistant is awake! Say your command (e.g. "turn on lights", "శుభరాత్రి").`
                  : `Say "Hey Jarvis", "Smart Home", "హలో", or "नमस्ते" anytime to activate hands-free!`
                : "Turn on hands-free mode to wake the assistant by voice without clicking the mic button."}
            </p>
          </div>
        </div>

        <div className="wake-word-right">
          <select
            className="wake-select-box"
            value={selectedWakePresetId}
            onChange={(e) => setSelectedWakePresetId(e.target.value)}
            disabled={isProcessing}
            title="Select wake keyword preset"
          >
            {WAKE_WORD_PRESETS.map(w => (
              <option key={w.id} value={w.id}>{w.label}</option>
            ))}
          </select>

          <button
            className={`wake-switch-btn ${wakeWordEnabled ? 'active' : ''}`}
            onClick={toggleWakeWord}
            title={wakeWordEnabled ? "Disable Hands-Free Mode" : "Enable Hands-Free Mode"}
          >
            <Zap size={14} />
            <span>{wakeWordEnabled ? 'Hands-Free ON' : 'Turn Hands-Free ON'}</span>
          </button>
        </div>
      </div>

      {/* Hero Visualizer / Mic Orb */}
      <div className={`voice-hero glass ${wakeStage === 'AWAKE' ? 'wake-triggered-glow' : ''}`}>
        <div className="voice-orb-wrapper">
          {/* Animated pulse rings */}
          <div className={`pulse-ring ring-1 ${isSpeaking ? 'speaking' : wakeStage === 'AWAKE' ? 'awake' : isListening ? 'listening' : isProcessing ? 'processing' : ''}`} />
          <div className={`pulse-ring ring-2 ${isSpeaking ? 'speaking' : wakeStage === 'AWAKE' ? 'awake' : isListening ? 'listening' : isProcessing ? 'processing' : ''}`} />
          <div className={`pulse-ring ring-3 ${isSpeaking ? 'speaking' : wakeStage === 'AWAKE' ? 'awake' : isListening ? 'listening' : isProcessing ? 'processing' : ''}`} />

          <button
            className={`voice-mic-orb ${isSpeaking ? 'speaking' : wakeStage === 'AWAKE' ? 'awake' : isListening ? 'listening' : isProcessing ? 'processing' : ''}`}
            onClick={handleOrbClick}
            disabled={isProcessing}
            aria-label={isListening ? "Stop listening and send" : "Start speaking"}
          >
            {isSpeaking ? (
              <Volume2 size={36} className="mic-icon speaking-pulse" />
            ) : wakeStage === 'AWAKE' ? (
              <Sparkles size={36} className="mic-icon awake-pulse" />
            ) : isListening ? (
              <MicOff size={36} className="mic-icon active" />
            ) : (
              <Mic size={36} className="mic-icon" />
            )}
          </button>
        </div>

        <div className="voice-orb-status">
          <div className="status-label-badge">
            <span className={`status-indicator-dot ${isSpeaking ? 'speaking' : wakeStage === 'AWAKE' ? 'awake' : isListening ? 'listening' : isProcessing ? 'processing' : 'ready'}`} />
            <span className="status-text">
              {isSpeaking
                ? 'Speaking response in native voice...'
                : wakeStage === 'AWAKE'
                  ? '⚡ Wake Word Active: Speak your smart home command now!'
                  : isListening 
                    ? wakeWordEnabled
                      ? `Listening hands-free in ${LANG_NAME_MAP[currentLangKey] || 'selected language'} (Say "Hey Jarvis" / "హలో")`
                      : `Listening in ${LANG_NAME_MAP[currentLangKey] || 'selected language'}... Speak now`
                    : isProcessing 
                      ? 'Processing command with Gemini AI...' 
                      : `Click microphone to speak in ${LANG_NAME_MAP[currentLangKey] || 'selected language'}`}
            </span>
          </div>

          {/* Live Transcript Preview Box with Instant Send Button */}
          {transcriptPreview && (
            <div className="live-transcript-box">
              <span className="transcript-prefix">"</span>
              <span className="transcript-content">{transcriptPreview}</span>
              <span className="transcript-suffix">"</span>
              
              <button 
                className="transcript-send-btn"
                onClick={() => {
                  if (!isExecutingRef.current && transcriptPreview) {
                    isExecutingRef.current = true;
                    clearSilenceTimer();
                    clearAwakeTimeout();
                    finalTranscriptRef.current = '';
                    setTranscriptPreview('');
                    executeCommand(transcriptPreview);
                  }
                }}
                title="Send recognized speech now"
              >
                <span>Send Now</span>
                <ArrowRight size={13} />
              </button>
            </div>
          )}

          {/* Error Message */}
          {errorMessage && (
            <div className="voice-error-banner">
              <AlertCircle size={16} />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>
      </div>

      {/* Quick Action Scene Chips */}
      <div className="quick-commands-section">
        <span className="quick-commands-title">
          Suggested Commands ({LANG_NAME_MAP[currentLangKey] || 'Commands'}):
        </span>
        <div className="quick-chips-scroll">
          {quickCommands.map((cmd, idx) => {
            const Icon = cmd.icon;
            return (
              <button
                key={idx}
                className="command-chip glass"
                onClick={() => executeCommand(cmd.query)}
                disabled={isProcessing || isListening}
              >
                <Icon size={14} className="chip-icon" />
                <span>{cmd.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Conversation Feed */}
      <div className="voice-chat-feed glass">
        <div className="chat-messages-scroll">
          {messages.map((msg) => (
            <div 
              key={msg.id} 
              className={`chat-message-row ${msg.sender === 'user' ? 'user-row' : 'assistant-row'}`}
            >
              <div className="message-avatar">
                {msg.sender === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>

              <div className={`message-bubble ${msg.sender === 'user' ? 'user-bubble' : 'assistant-bubble'} ${msg.isError ? 'error-bubble' : ''}`}>
                <div className="message-bubble-header">
                  {msg.sender === 'assistant' && msg.language && (
                    <div className="msg-lang-pill">
                      <Globe size={11} />
                      <span>{LANG_NAME_MAP[msg.language.split('-')[0]] || msg.language}</span>
                    </div>
                  )}
                  {msg.sender === 'assistant' && !msg.isError && (
                    <button
                      className="replay-voice-btn"
                      onClick={() => speakResponse(msg.text, msg.language)}
                      title="Replay authentic spoken voice"
                    >
                      <Volume2 size={13} />
                    </button>
                  )}
                </div>
                <p className="message-text">{msg.text}</p>

                {/* Device Actions Badges */}
                {msg.actions && msg.actions.length > 0 && (
                  <div className="message-actions-grid">
                    {msg.actions.map((act, aIdx) => (
                      <div key={aIdx} className={`action-result-badge ${act.success ? 'success' : 'failed'}`}>
                        <CheckCircle2 size={12} />
                        <span className="action-device-name">{formatDeviceName(act.device)}:</span>
                        <span className="action-status-val">{act.target_status}</span>
                      </div>
                    ))}
                  </div>
                )}

                <span className="message-timestamp">{msg.timestamp}</span>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Text Input Bar */}
        <div className="voice-input-bar">
          <button
            className={`input-mic-btn ${isListening ? 'active' : ''}`}
            onClick={handleOrbClick}
            title={isListening ? "Stop listening and send" : "Click to speak"}
            disabled={isProcessing}
          >
            {isListening ? <MicOff size={18} /> : <Mic size={18} />}
          </button>

          <input
            type="text"
            className="voice-text-input"
            placeholder={
              wakeStage === 'AWAKE'
                ? "Listening for command... Speak now..."
                : isListening 
                  ? wakeWordEnabled ? `Listening hands-free... Say "Hey Jarvis" or "హలో"...` : "Listening... Speak now..." 
                  : currentLangKey === 'te'
                    ? "కమాండ్ టైప్ చేయండి (ఉదా. 'లైట్ ఆన్ చేయి', 'శుభరాత్రి')..."
                    : currentLangKey === 'hi'
                      ? "कमांड टाइप करें (उदा. 'लिविंग रूम लाइट चालू करो', 'शुभ रात्रि')..."
                      : currentLangKey === 'es'
                        ? "Escribe un comando (ej. 'Apaga todas las luces', 'Buenas noches')..."
                        : "Type a smart home command (e.g. 'Turn off all lights', 'Good night')..."
            }
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isProcessing}
          />

          <button
            className="voice-send-btn"
            onClick={() => executeCommand()}
            disabled={!inputText.trim() || isProcessing}
            title="Send command"
          >
            <Send size={16} />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  );
}
