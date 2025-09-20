class WordLearningApp {
    constructor() {
        this.currentWord = null;
        this.wordsLearned = 0;
        this.correctAnswers = 0;
        this.isLoading = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadNewWord();
    }
    
    initializeElements() {
        this.wordText = document.getElementById('word-text');
        this.wordDefinition = document.getElementById('word-definition');
        this.wordLevel = document.getElementById('word-level');
        this.wordImage = document.getElementById('word-image');
        this.sentenceText = document.getElementById('sentence-text');
        this.answerInput = document.getElementById('answer-input');
        this.checkAnswerBtn = document.getElementById('check-answer-btn');
        this.newWordBtn = document.getElementById('new-word-btn');
        this.generateImageBtn = document.getElementById('generate-image-btn');
        this.generateSentenceBtn = document.getElementById('generate-sentence-btn');
        this.feedback = document.getElementById('feedback');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.wordsLearnedElement = document.getElementById('words-learned');
        this.correctAnswersElement = document.getElementById('correct-answers');
        this.levelSelect = document.getElementById('level-select');
    }
    
    bindEvents() {
        this.newWordBtn.addEventListener('click', () => this.loadNewWord());
        this.generateImageBtn.addEventListener('click', () => this.generateImage());
        this.generateSentenceBtn.addEventListener('click', () => this.generateSentence());
        this.checkAnswerBtn.addEventListener('click', () => this.checkAnswer());
        this.levelSelect.addEventListener('change', () => this.loadNewWord());
        
        this.answerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.checkAnswer();
            }
        });
    }
    
    async loadNewWord() {
        this.showLoading();
        
        try {
            const selectedLevel = this.levelSelect.value;
            const url = selectedLevel ? `/api/word/${selectedLevel}` : '/api/word';
            const response = await fetch(url);
            const word = await response.json();
            
            this.currentWord = word;
            this.displayWord(word);
            this.clearFeedback();
            this.answerInput.value = '';
            
            // Otomatik olarak görsel ve cümle oluştur
            await Promise.all([
                this.generateImage(),
                this.generateSentence()
            ]);
            
        } catch (error) {
            console.error('Kelime yüklenirken hata:', error);
            this.showError('Kelime yüklenirken bir hata oluştu.');
        } finally {
            this.hideLoading();
        }
    }
    
    displayWord(word) {
        const shownWord = (word.lemma && typeof word.lemma === 'string' && word.lemma.trim()) ? word.lemma : word.word;
        this.wordText.textContent = shownWord;
        this.wordDefinition.textContent = word.definition;
        this.wordLevel.innerHTML = `<span class="level-badge">${word.level}</span>`;
    }
    
    async generateImage() {
        if (!this.currentWord) return;
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/generate-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    word: this.currentWord.word,
                    definition: this.currentWord.definition
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayImage(result.image_url, result.description, result.backup_url);
                if (result.visual_concept) {
                    console.log(`Gemini visual concept: ${result.visual_concept}`);
                }
            } else {
                this.showError('Görsel oluşturulurken bir hata oluştu.');
            }
            
        } catch (error) {
            console.error('Görsel oluşturma hatası:', error);
            this.showError('Görsel oluşturulurken bir hata oluştu.');
        } finally {
            this.hideLoading();
        }
    }
    
    displayImage(imageUrl, description, backupUrl = null) {
        const img = new Image();
        
        // Resim yüklendiğinde
        img.onload = () => {
            this.wordImage.innerHTML = `
                <img src="${imageUrl}" alt="${description}" 
                     style="width: 100%; height: 100%; object-fit: cover; border-radius: 15px;">
            `;
        };
        
        // Resim yüklenemediyse backup kullan
        img.onerror = () => {
            const fallbackText = (this.currentWord?.lemma || this.currentWord?.word || 'IMAGE').toUpperCase();
            const fallbackUrl = backupUrl || `https://via.placeholder.com/400x300/667eea/FFFFFF?text=${fallbackText}`;
            this.wordImage.innerHTML = `
                <img src="${fallbackUrl}" alt="${description}" 
                     style="width: 100%; height: 100%; object-fit: cover; border-radius: 15px;">
            `;
        };
        
        // Loading göster
        this.wordImage.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: white;">
                <i class="fas fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 10px;"></i>
                <p>Resim yükleniyor...</p>
            </div>
        `;
        
        // Resmi yüklemeye başla
        img.src = imageUrl;
    }
    
    async generateSentence() {
        if (!this.currentWord) return;
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/generate-sentence', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    word: this.currentWord.word,
                    definition: this.currentWord.definition
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.sentenceText.textContent = result.sentence;
                this.currentWord.sentence = result.sentence;
                this.currentWord.answer = result.answer;
            } else {
                this.showError('Cümle oluşturulurken bir hata oluştu.');
            }
            
        } catch (error) {
            console.error('Cümle oluşturma hatası:', error);
            this.showError('Cümle oluşturulurken bir hata oluştu.');
        } finally {
            this.hideLoading();
        }
    }
    
    async checkAnswer() {
        if (!this.currentWord || !this.currentWord.answer) {
            this.showError('Lütfen önce bir cümle oluşturun.');
            return;
        }
        
        const userAnswer = this.answerInput.value.trim();
        if (!userAnswer) {
            this.showError('Lütfen bir cevap girin.');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/check-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    answer: userAnswer,
                    correct_answer: this.currentWord.answer
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (result.is_correct) {
                    this.showSuccess('Tebrikler! Doğru cevap! 🎉');
                    this.correctAnswers++;
                    this.wordsLearned++;
                    this.updateStats();
                    
                    // 2 saniye sonra yeni kelime yükle
                    setTimeout(() => {
                        this.loadNewWord();
                    }, 2000);
                } else {
                    this.showError(`Yanlış cevap. Doğru cevap: "${result.correct_answer}"`);
                }
            } else {
                this.showError('Cevap kontrol edilirken bir hata oluştu.');
            }
            
        } catch (error) {
            console.error('Cevap kontrol hatası:', error);
            this.showError('Cevap kontrol edilirken bir hata oluştu.');
        } finally {
            this.hideLoading();
        }
    }
    
    showSuccess(message) {
        this.feedback.textContent = message;
        this.feedback.className = 'feedback correct show';
        this.answerInput.value = '';
    }
    
    showError(message) {
        this.feedback.textContent = message;
        this.feedback.className = 'feedback incorrect show';
    }
    
    clearFeedback() {
        this.feedback.className = 'feedback';
    }
    
    showLoading() {
        this.isLoading = true;
        this.loadingOverlay.classList.add('show');
        this.disableButtons();
    }
    
    hideLoading() {
        this.isLoading = false;
        this.loadingOverlay.classList.remove('show');
        this.enableButtons();
    }
    
    disableButtons() {
        this.newWordBtn.disabled = true;
        this.generateImageBtn.disabled = true;
        this.generateSentenceBtn.disabled = true;
        this.checkAnswerBtn.disabled = true;
        this.answerInput.disabled = true;
    }
    
    enableButtons() {
        this.newWordBtn.disabled = false;
        this.generateImageBtn.disabled = false;
        this.generateSentenceBtn.disabled = false;
        this.checkAnswerBtn.disabled = false;
        this.answerInput.disabled = false;
    }
    
    updateStats() {
        this.wordsLearnedElement.textContent = this.wordsLearned;
        this.correctAnswersElement.textContent = this.correctAnswers;
    }
}

// Uygulamayı başlat
document.addEventListener('DOMContentLoaded', () => {
    new WordLearningApp();
});

// Klavye kısayolları
document.addEventListener('keydown', (e) => {
    if (e.key === 'n' || e.key === 'N') {
        document.getElementById('new-word-btn').click();
    } else if (e.key === 'i' || e.key === 'I') {
        document.getElementById('generate-image-btn').click();
    } else if (e.key === 's' || e.key === 'S') {
        document.getElementById('generate-sentence-btn').click();
    }
});
