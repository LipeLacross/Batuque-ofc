import sys
import numpy as np
import cv2
import time
from pygame import mixer
import pygame
import subprocess

pygame.init()

logo_image = pygame.image.load("src/Images/tela inicial/logo.png")

largura, altura = 1920, 1080
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

def loading_screen(tela, loading_progress):
    tela.fill(PRETO)
    tela.blit(logo_image, (largura // 3 - logo_image.get_width() // 3.5, altura // 3 - logo_image.get_height() // 3))
    pygame.display.flip()

def run_batuque(screen):
    # Configurações de cor para detecção
    h_low, h_high = 146, 172
    s_low, s_high = 116, 255
    v_low, v_high = 123, 255
    pinkLower = (h_low, s_low, v_low)
    pinkUpper = (h_high, s_high, v_high)

    # Configurações da música
    mixer.init()
    mixer.music.load('src/sounds/Tutorial 1.wav')

    def init_mixer_and_play_music(music):
        mixer.init()
        mixer.music.load(music)
        mixer.music.play()

    # Definindo os tempos das batidas
    Bumbo_times = [2.6, 3, 4.1, 4.4, 5.6, 5.9, 7, 7.4, 8.5, 8.9, 10, 10.35, 11.4, 11.8, 12.7, 13.1, 14.3, 14.7, 15.8, 16.2, 17.3, 17.65, 18.75, 19.1, 20.2, 20.6, 21.7, 22.1, 23.1, 23.5, 24.55, 24.95, 26.05, 26.4, 27.45, 27.85, 28.95, 29.3, 30.35, 30.65, 31.87, 32.25, 33.35, 33.75, 34.85, 35.25]
    Caixa_times = [3.35, 4.8, 6.3, 7.8, 9.2, 10.7, 12.1, 13.6, 15.1, 16.5, 18.05, 19.5, 20.95, 22.4, 23.8, 25.3, 26.7, 28.2, 29.65, 31.15, 32.65, 34.1, 35.55]
    
    last_played_time = [0, 0, 0, 0, 0]
    cooldown = 0.5  # Tempo em segundos entre toques

    # Estado para verificar se o som já foi tocado
    sound_played = [False, False, False, False, False]

    drum_sounds = [
        mixer.Sound('src/sounds/Chimbal/Chimbal.mp3'),
        mixer.Sound('src/sounds/Caixa/Caixa.mp3'),
        mixer.Sound('src/sounds/Bumbo/Bumbo.wav'),
        mixer.Sound('src/sounds/Crash/Crash.mp3'),
        mixer.Sound('src/sounds/Caixa2/Caixa2.mp3')
    ]

    def state_machine(sound_index):
        current_time = time.time()
        if current_time - last_played_time[sound_index] >= cooldown:
            drum_sounds[sound_index].play()
            last_played_time[sound_index] = current_time
            sound_played[sound_index] = True

    def calc_mask(frame, lower, upper):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return cv2.inRange(hsv, lower, upper)

    def ROI_analysis(roi, sound_index, lower, upper, min_value=30):
        mask = calc_mask(roi, lower, upper)
        summation = np.sum(mask)

        if summation >= min_value:
            if not sound_played[sound_index]:
                state_machine(sound_index)
        else:
            sound_played[sound_index] = False

        return mask

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, largura)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, altura)

    if not camera.isOpened():
        print("Erro ao abrir a câmera")
        sys.exit()

    instruments = ['Chimbal.png', 'Caixa.png', 'Bumbo.png', 'Crash.png', 'Caixa2.png']
    instrument_images = []

    for img in instruments:
        image = cv2.imread(f'./src/Images/{img}', cv2.IMREAD_UNCHANGED)
        if image is None:
            print(f"Erro ao carregar imagem: {img}")
        else:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            image = cv2.flip(image, 1)
            instrument_images.append(cv2.resize(image, (200, 150), interpolation=cv2.INTER_CUBIC))

    # Posições dos instrumentos ajustadas
    H, W = 1080, 1920
    centers = [
        (int(H * 0.4), int(W * 0.1)),  # Chimbal
        (int(H * 0.6), int(W * 0.6)),  # Caixa
        (int(H * 0.7), int(W * 0.4)),  # Bumbo
        (int(H * 0.4), int(W * 0.7)),  # Crash
        (int(H * 0.6), int(W * 0.2))   # Caixa espelhada
    ]

    sizes = [(150, 200), (150, 200), (200, 200), (150, 200), (150, 200)]  # Ajustar o tamanho para corresponder à nova orientação

    ROIs = [(center[0] - size[0] // 2, center[1] - size[1] // 2, center[0] + size[0] // 2, center[1] + size[1] // 2) for center, size in zip(centers, sizes)]

    init_mixer_and_play_music('src/sounds/Tutorial 1.wav')

    start_time = time.time()

    # Variável para verificar se o tutorial está em andamento
    tutorial_iniciado = False
    running = True
    while running:
        ret, frame = camera.read()
        while not ret or frame is None or frame.size == 0:
            ret, frame = camera.read()
            print("Erro ao capturar imagem da câmera")
            break

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Rotacionar a imagem da câmera
        frame = cv2.resize(frame, (altura, largura))

        current_time = time.time() - start_time

        for i, (top_x, top_y, bottom_x, bottom_y) in enumerate(ROIs):
            roi = frame[top_y:bottom_y, top_x:bottom_x]
            mask = ROI_analysis(roi, i, pinkLower, pinkUpper)

        # Atualizar batidas
        for beat_time in Bumbo_times:
            if abs(current_time - beat_time) < 0.1:
                center_x, center_y = centers[2]
                radius = int(50 + 50 * (1 - abs(current_time - beat_time) / 0.1))
                cv2.circle(frame, (center_x, center_y), radius, (255, 0, 255), -1)

        for beat_time in Caixa_times:
            if abs(current_time - beat_time) < 0.1:
                center_x, center_y = centers[1]
                radius = int(50 + 50 * (1 - abs(current_time - beat_time) / 0.1))
                cv2.circle(frame, (center_x, center_y), radius, (255, 0, 255), -1)

        for i, (top_x, top_y, bottom_x, bottom_y) in enumerate(ROIs):
            roi = frame[top_y:bottom_y, top_x:bottom_x]
            overlay = instrument_images[i]
            overlay_resized = cv2.resize(overlay, (roi.shape[1], roi.shape[0]))

            if overlay_resized.shape[2] == 4:
                b, g, r, a = cv2.split(overlay_resized)
                overlay_rgb = cv2.merge((b, g, r))
                alpha_mask = a / 255.0 * 0.5
                alpha_inv = 1.0 - alpha_mask

                for c in range(0, 3):
                    frame[top_y:bottom_y, top_x:bottom_x, c] = (alpha_mask * overlay_rgb[:, :, c] +
                                                                alpha_inv * frame[top_y:bottom_y, top_x:bottom_x, c])
            else:
                frame[top_y:bottom_y, top_x:bottom_x] = cv2.addWeighted(overlay_resized, 0.5, roi, 0.5, 0)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame)
        screen.blit(frame_surface, (0, 0))
        pygame.display.flip()

        # Captura eventos do Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Se a janela for fechada
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # Se a tecla ESC for pressionada
                if not tutorial_iniciado:
                    tutorial_iniciado = True  # Marcar que o tutorial foi iniciado
                else:
                    running = False  # Encerra o loop após terminar o tutorial

                    # Rodar interface.py após o ESC
                    subprocess.Popen(['python', 'interface.py']) 

    # Liberar câmera e fechar o Pygame corretamente
    camera.release()
    pygame.quit()
    cv2.destroyAllWindows()
