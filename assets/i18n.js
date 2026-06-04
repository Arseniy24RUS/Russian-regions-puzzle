(function(){
  "use strict";

  var supported = ["en", "ru"];
  var script = document.currentScript;
  var localesPath = script && script.getAttribute("data-locales-path") || "locales";
  var messages = {};
  var loading = {};
  var state = {
    language: detectLanguage()
  };

  function normalizeLanguage(value){
    var lang = String(value || "").toLowerCase().slice(0, 2);
    return supported.indexOf(lang) >= 0 ? lang : null;
  }

  function detectLanguage(){
    try {
      var stored = normalizeLanguage(localStorage.getItem("lang"));
      if (stored) return stored;
    } catch (e) {}

    var list = [];
    if (navigator.languages && navigator.languages.length) list = Array.prototype.slice.call(navigator.languages);
    if (navigator.language) list.push(navigator.language);
    return list.some(function(item){ return String(item || "").toLowerCase().indexOf("ru") >= 0; }) ? "ru" : "en";
  }

  function getPath(obj, key){
    return String(key || "").split(".").reduce(function(acc, part){
      return acc && Object.prototype.hasOwnProperty.call(acc, part) ? acc[part] : undefined;
    }, obj);
  }

  function format(value, params){
    if (value === undefined || value === null) return value;
    return String(value).replace(/\{(\w+)\}/g, function(match, name){
      return params && Object.prototype.hasOwnProperty.call(params, name) ? params[name] : match;
    });
  }

  function loadLanguage(lang){
    lang = normalizeLanguage(lang) || "en";
    if (messages[lang]) return Promise.resolve(messages[lang]);
    if (loading[lang]) return loading[lang];
    loading[lang] = fetch(localesPath + "/" + lang + ".json")
      .then(function(res){
        if (!res.ok) throw new Error("Locale not found: " + lang);
        return res.json();
      })
      .then(function(data){
        messages[lang] = data || {};
        return messages[lang];
      });
    return loading[lang];
  }

  function t(key, params, fallback){
    var value = getPath(messages[state.language], key);
    if (value === undefined && messages.en) value = getPath(messages.en, key);
    if (value === undefined && messages.ru) value = getPath(messages.ru, key);
    if (value === undefined) value = fallback !== undefined ? fallback : key;
    return format(value, params || {});
  }

  function translateMapValue(mapName, value, fallback){
    var table = messages[state.language] && messages[state.language][mapName];
    if (table && Object.prototype.hasOwnProperty.call(table, value)) return table[value];
    return fallback !== undefined ? fallback : value;
  }

  function getLanguage(){
    return state.language;
  }

  function query(root, selector){
    var found = [];
    if (!root) return found;
    if (root.nodeType === 1 && root.matches && root.matches(selector)) found.push(root);
    if (root.querySelectorAll) found = found.concat(Array.prototype.slice.call(root.querySelectorAll(selector)));
    return found;
  }

  function bindLanguageToggle(button){
    if (button.dataset.i18nBound === "true") return;
    button.dataset.i18nBound = "true";
    button.addEventListener("click", function(){ toggleLanguage(); });
  }

  function apply(root){
    root = root || document;
    document.documentElement.lang = state.language;
    document.title = t("meta.title");

    query(root, "[data-i18n]").forEach(function(node){
      node.textContent = t(node.getAttribute("data-i18n"));
    });
    query(root, "[data-i18n-placeholder]").forEach(function(node){
      node.setAttribute("placeholder", t(node.getAttribute("data-i18n-placeholder")));
    });
    query(root, "[data-i18n-title]").forEach(function(node){
      node.setAttribute("title", t(node.getAttribute("data-i18n-title")));
    });
    query(root, "[data-i18n-aria-label]").forEach(function(node){
      node.setAttribute("aria-label", t(node.getAttribute("data-i18n-aria-label")));
    });
    query(root, "[data-testid='language-toggle']").forEach(function(button){
      bindLanguageToggle(button);
      var targetKey = state.language === "ru" ? "language.toggleToEnglish" : "language.toggleToRussian";
      button.textContent = state.language === "ru" ? "EN" : "RU";
      button.setAttribute("aria-label", t(targetKey));
      button.setAttribute("title", t(targetKey));
    });

    return state.language;
  }

  function emitChange(){
    var event;
    try {
      event = new CustomEvent("app:i18n:changed", { detail: { language: state.language } });
    } catch (e) {
      event = document.createEvent("CustomEvent");
      event.initCustomEvent("app:i18n:changed", false, false, { language: state.language });
    }
    window.dispatchEvent(event);
  }

  function setLanguage(lang){
    lang = normalizeLanguage(lang) || "en";
    return loadLanguage(lang).then(function(){
      state.language = lang;
      try { localStorage.setItem("lang", lang); } catch (e) {}
      apply(document);
      emitChange();
      return state.language;
    });
  }

  function toggleLanguage(){
    return setLanguage(state.language === "ru" ? "en" : "ru");
  }

  var ready = loadLanguage(state.language).then(function(){
    apply(document);
    return state.language;
  });

  window.AppI18n = {
    t: t,
    getLanguage: getLanguage,
    setLanguage: setLanguage,
    toggleLanguage: toggleLanguage,
    apply: apply,
    ready: ready,
    translateRegion: function(value, fallback){ return translateMapValue("regions", value, fallback); },
    translateFederalDistrict: function(value, fallback){ return translateMapValue("federalDistricts", value, fallback); }
  };
})();
