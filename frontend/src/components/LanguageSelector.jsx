import { useState, useRef, useEffect } from 'react';
import { Globe, Check, ChevronDown } from 'lucide-react';

const languages = [
  { id: 'auto', label: 'Auto-Detect', icon: '🌐', desc: 'Matches your language' },
  { id: 'english', label: 'English', icon: '🇬🇧', desc: 'Always in English' },
  { id: 'hindi', label: 'हिन्दी', icon: '🇮🇳', desc: 'हमेशा हिन्दी में' },
  { id: 'hinglish', label: 'Hinglish', icon: '🗣️', desc: 'Hindi + English mix' },
];

export default function LanguageSelector({ activeLanguage, onSwitch }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const activeLang = languages.find((l) => l.id === activeLanguage) || languages[0];

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        id="language-selector-btn"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium
                   glass border border-border text-text-secondary
                   hover:bg-bg-tertiary hover:text-text-primary hover:border-border-hover
                   transition-all duration-200"
        title="Change response language"
      >
        <Globe className="w-3.5 h-3.5" />
        <span>{activeLang.label}</span>
        <ChevronDown
          className={`w-3 h-3 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div
          className="absolute right-0 top-full mt-1.5 w-52 rounded-xl overflow-hidden
                      glass border border-border shadow-xl shadow-black/30
                      z-50 animate-fade-in-up"
        >
          {languages.map((lang) => (
            <button
              key={lang.id}
              id={`lang-option-${lang.id}`}
              onClick={() => {
                onSwitch(lang.id);
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 text-left transition-colors duration-150
                ${
                  activeLanguage === lang.id
                    ? 'bg-accent/10 text-accent'
                    : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                }`}
            >
              <span className="text-lg">{lang.icon}</span>
              <div className="flex flex-col">
                <span className="text-xs font-medium">{lang.label}</span>
                <span className="text-[10px] text-text-muted">{lang.desc}</span>
              </div>
              {activeLanguage === lang.id && (
                <Check className="w-3.5 h-3.5 ml-auto text-accent" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
