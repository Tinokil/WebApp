class QuestGame {
  constructor() {
    const savedState = localStorage.getItem('questGameState');
    this.state = {
      currentChapter: 'chapter1',
      currentScene: null,
      language: navigator.language.startsWith('ru') ? 'ru' : 'en',
      soundEnabled: false,
      history: [],
      audio: new Audio('assets/sound.mp3'),
      clickSound: new Audio('assets/click.mp3'),
      ...(savedState && JSON.parse(savedState)),
      audio: new Audio('assets/sound.mp3'),
      clickSound: new Audio('assets/click.mp3')
    };

    this.elements = {
      chapterTitle: document.querySelector('.chapter-title'),
      sceneContent: document.querySelector('.scene-content'),
      contentContainer: document.querySelector('.content'),
      navigation: document.querySelector('.navigation'),
      backBtn: document.querySelector('.back'),
      soundBtn: document.querySelector('.sound img'),
      soundToggle: document.querySelector('.sound')
    };

    if (savedState?.audioTime) {
      this.state.audio.currentTime = JSON.parse(savedState).audioTime;
    }

    this.loadInitialScene();
    this.setupEventListeners();
  }

  async loadInitialScene() {
    try {
      if (this.state.currentScene) {
        await this.loadScene(this.state.currentScene, true);
      } else {
        const chapter = await this.loadChapter(this.state.currentChapter);
        chapter?.startScene 
          ? await this.loadScene(chapter.startScene)
          : this.showError();
      }
    } catch (error) {
      console.error('Initial load failed:', error);
      this.showError();
    }
  }

  async loadScene(sceneId, isBack = false) {
    if (!sceneId) return;

    try {
      const [chapter, scene] = sceneId.includes(':') 
        ? sceneId.split(':') 
        : [this.state.currentChapter, sceneId];

      const chapterData = await this.loadChapter(chapter);
      if (!chapterData?.scenes?.[scene]) throw new Error('Scene not found');

      // Проверяем, есть ли в текущей сцене кнопка с типом 'failed'
      const currentSceneHasFailed = chapterData.scenes[scene]?.btns?.some(b => b.type === 'failed');
      
      if (!isBack && this.state.currentScene && !currentSceneHasFailed) {
        this.state.history.push({
          chapter: this.state.currentChapter,
          scene: this.state.currentScene
        });
      }

      // Если это сцена с провалом, очищаем историю
      if (currentSceneHasFailed) {
        this.state.history = [];
      }

      this.state.currentChapter = chapter;
      this.state.currentScene = scene;
      this.saveState();
      this.renderScene(chapterData, scene);
    } catch (error) {
      console.error('Scene load error:', error);
      this.showRetry(sceneId, isBack);
    }
  }

  renderScene(chapter, sceneId) {
    const scene = chapter.scenes[sceneId];
    this.elements.chapterTitle.textContent = chapter.title[this.state.language];
    
    this.elements.sceneContent.innerHTML = '';
    this.elements.contentContainer.style.padding = scene.text ? '20px 18px' : '0';

    if (scene.image) {
      const img = new Image();
      img.src = scene.image;
      img.className = 'scene-image';
      img.onerror = () => scene.text && this.renderText(scene.text);
      this.elements.sceneContent.appendChild(img);
    }

    if (scene.text) {
      this.renderText(scene.text);
    }

    this.renderButtons(scene, sceneId);
    this.updateBackButton(scene);
  }

  renderText(text) {
    const div = document.createElement('div');
    div.className = 'text';
    div.textContent = text[this.state.language];
    this.elements.sceneContent.appendChild(div);
  }

  renderButtons(scene, currentSceneId) {
    this.elements.navigation.innerHTML = '';
    
    if (scene.btns?.length) {
      scene.btns.forEach(btn => {
        const button = document.createElement('button');
        button.className = btn.type === 'choice' ? 'button' : 'next_button';
        button.textContent = btn.text[this.state.language];
        
        button.addEventListener('click', () => {
          this.playSound(this.state.clickSound);
          this.animateButton(button);
          setTimeout(() => {
            if (btn.type === 'failed') {
              this.state.history = [];
            }
            this.loadScene(btn.nextScene);
          }, 150);
        });
        
        this.elements.navigation.appendChild(button);
      });
    } else {
      const button = document.createElement('button');
      button.className = 'next_button';
      button.textContent = this.state.language === 'ru' ? 'Далее' : 'Next';
      
      button.addEventListener('click', () => {
        this.playSound(this.state.clickSound);
        this.animateButton(button);
        setTimeout(() => {
          const num = parseInt(currentSceneId.replace(/\D/g, '')) || 0;
          this.loadScene(`${this.state.currentChapter}:scene${num + 1}`);
        }, 150);
      });
      
      this.elements.navigation.appendChild(button);
    }
  }

  updateBackButton(scene) {
    const hasFailed = scene.btns?.some(btn => btn.type === 'failed');
    const isFirstScene = this.state.history.length === 0;
    
    // Скрываем кнопку "Назад" если:
    // 1. Это первая сцена
    // 2. В текущей сцене есть кнопка с типом 'failed'
    // 3. Нет истории переходов
    this.elements.backBtn.style.display = 
      (hasFailed || isFirstScene) ? 'none' : 'block';
  }

  navigateBack() {
    if (!this.state.history.length) return;
    
    const lastScene = this.state.history.pop();
    this.loadScene(`${lastScene.chapter}:${lastScene.scene}`, true);
  }

  async loadChapter(chapterId) {
    try {
      const filename = chapterId.endsWith('.json') ? chapterId : `${chapterId}.json`;
      const response = await fetch(`chapters/${filename}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`Chapter load error: ${chapterId}`, error);
      return chapterId !== 'chapter1' ? this.loadChapter('chapter1') : null;
    }
  }

  setupEventListeners() {
    this.elements.soundToggle.addEventListener('click', () => {
      this.state.soundEnabled = !this.state.soundEnabled;
      this.state.audio[this.state.soundEnabled ? 'play' : 'pause']();
      this.elements.soundBtn.src = `assets/${this.state.soundEnabled ? 'on' : 'off'}_sound.png`;
      this.saveState();
    });

    this.elements.backBtn.addEventListener('click', () => {
      this.playSound(this.state.clickSound);
      this.navigateBack();
    });
  }

  playSound(sound) {
    if (this.state.soundEnabled) {
      sound.currentTime = 0;
      sound.play().catch(console.error);
    }
  }

  animateButton(button) {
    button.style.transform = 'scale(0.95)';
    setTimeout(() => button.style.transform = '', 150);
  }

  saveState() {
    const state = {
      ...this.state,
      audioTime: this.state.audio.currentTime,
      audio: undefined,
      clickSound: undefined
    };
    localStorage.setItem('questGameState', JSON.stringify(state));
  }

  showRetry(sceneId, isBack) {
    this.elements.sceneContent.innerHTML = `
      <div class="error">
        <p>${this.state.language === 'ru' ? 'Ошибка загрузки' : 'Loading error'}</p>
        <button class="retry-button">${this.state.language === 'ru' ? 'Повторить' : 'Retry'}</button>
      </div>
    `;
    
    document.querySelector('.retry-button')?.addEventListener('click', () => {
      this.loadScene(sceneId, isBack);
    });
  }

  showError() {
    this.elements.sceneContent.innerHTML = `
      <div class="error-message">
        <p>${this.state.language === 'ru' ? 'Ошибка' : 'Error'}</p>
      </div>
    `;
  }
}

document.addEventListener('DOMContentLoaded', () => new QuestGame());