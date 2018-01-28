import pygame
from pygame.locals import *
from pydub import AudioSegment
from math import pi, fabs, floor
from stats import median
from random import choice, randint, uniform
from threading import Timer
import rhythm
import colors
import entity
import rhythm

FPS = 60
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

pygame.init()
pygame.display.set_caption('space rhythm relay')
pygame.display.set_icon(pygame.image.load('media/icon.png'))
pygame.mixer.pre_init(44100,-16,2, 512)
pygame.mixer.init()

signal_channel = pygame.mixer.Channel(0)
noise_channel = pygame.mixer.Channel(1)
player_channel = pygame.mixer.Channel(2)

background_color = colors.Color(0, 0, 0)

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
surface = pygame.Surface(screen.get_size())

font = pygame.font.SysFont("arial", 40)

if __name__ == '__main__':
        planet = entity.Planet(SCREEN_HEIGHT/2, SCREEN_WIDTH/2, 120, colors.Color(255, 255, 255))
        satellite = entity.Satellite(20, colors.Color(255, 0, 0), planet)
        broadcaster = entity.Satellite(30, colors.Color(0, 255, 0), planet)

        game_playing = True
        game_stage = 'generate'        
        wave = 0
        tempo_accuracy = 100
        tap_stack = []

        signal = rhythm.generate_phrase(60, [4, 4])
        kick = AudioSegment.from_wav('media/kick.wav')
        
        signal_audio = pygame.mixer.Sound(signal.to_audio(kick).raw_data)

        static = pygame.mixer.Sound('media/static.wav')
        snare = pygame.mixer.Sound('media/snare.wav')
        error = pygame.mixer.Sound('media/error.wav')

        announcements = [
                            pygame.mixer.Sound('media/Upper Left Quadrant.wav'), 
                            pygame.mixer.Sound('media/Upper Right Quadrant.wav'),
                            pygame.mixer.Sound('media/Lower Right Quadrant.wav'),
                            pygame.mixer.Sound('media/Lower Left Quadrant.wav')
                        ]
        
        noise_channel.play(static, loops=-1)

        while game_playing:
            ### Event based actions ###
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == KEYDOWN:
                    if event.key == K_SPACE and game_stage == 'input':
                        satellite.pulse(0, 5, 1/500)
                        if satellite.quadrant == goal_quadrant:
                            player_channel.play(snare)
                            tap_stack.append(pygame.time.get_ticks())
                        else:
                            player_channel.play(error)


            pressed = pygame.key.get_pressed()

            if pressed[K_LEFT]:
                satellite.orbit(-0.05)
            
            elif pressed[K_RIGHT]:
                satellite.orbit(0.05)

            #   Wave complications:
            #   Each successive wave makes the game 10bpm faster, up to a limit
            #   Waves above 5 have two bars
            #   Waves above 15 have three bars
            #   Waves above 8 have mixed time signatures
            #   Waves above 20 have randomized bpm
                    
            if game_stage == 'generate':
                wave_bpm = 200 + 10 * wave
                wave_bar_count = 1
                wave_bar_length_array = []
                goal_quadrant = randint(0, 3)

                if wave_bpm > 500:  # BPM capped at 500
                    wave_bpm = 500
                
                if wave > 15:  # How many bars will be in the phrase this wave?
                    wave_bar_count = 3
                elif wave > 5:
                    wave_bar_count = 2

                if wave >= 8:
                    for i in range(0, wave_bar_count - 1):
                        wave_bar_length_array.append(choice([3,4,7]))
                else:
                    wave_bar_length_array = [choice([3,4,4,7])] * wave_bar_count

                if wave > 20:
                    bpm = randint(80, 250)

                signal = rhythm.generate_phrase(wave_bpm, wave_bar_length_array)
                signal_audio = pygame.mixer.Sound(signal.to_audio(kick).raw_data)
                
                for i in signal.timings:
                    planet.pulse(int(floor(i)) + 1600, 10, 1/500)

                signal_channel.play(announcements[goal_quadrant])

                signal_channel.queue(signal_audio)

                game_stage = 'input'

            ### Gameplay actions ###
            if game_stage == 'input':
                #print(tap_stack, signal.timings, signal.length)
                if len(tap_stack) >= len(signal.timings):
                    adjusted_taps = []
                    offset = tap_stack[0]

                    for i in tap_stack:
                        adjusted_taps.append((i - offset)/2)  # Divided by two because

                    goal_delays = []
                    actual_delays = []
                    for i in range(1, len(adjusted_taps)):
                        actual_delays.append(adjusted_taps[i]-adjusted_taps[i-1])
                        goal_delays.append(signal.timings[i] - signal.timings[i-1])

                    median_goal = median(goal_delays)
                    median_actual = median(actual_delays)
                    tempo_accuracy = int(100*(median_actual/median_goal))

                    outlier = False

                    for i in range(0, len(actual_delays)):
                        if fabs(actual_delays[i]-goal_delays[i]) > 200:
                            outlier = True
                            break
                    
                    if not outlier:
                        if median_goal < median_actual + 20 and median_goal > median_actual - 50:
                            wave +=2
                        elif median_goal < median_actual + 70 and median_goal > median_actual - 1000:
                            wave +=1
                        elif (median_goal > median_actual + 200 or median_goal < median_actual - 1000) and wave != 0:
                            wave -= 1
                    elif wave != 0:
                        wave -= 1

                    tap_stack = []
                    game_stage = 'generate'
                

            ## General update actions ###

            distance = fabs(((satellite.angle + 0.25) % (2*pi) - pi)/pi)
            noise_channel.set_volume(distance)

            screen.fill(background_color.tuple)
            planet.draw(screen)
            satellite.draw(screen)

            accuracy_text = font.render('tempo accuracy: ' + str(tempo_accuracy) + '%', True, (255, 255, 255))
            wave_text = font.render('level '+ str(wave), True, (255, 255, 255))

            screen.blit(wave_text, (20, 50))
            screen.blit(accuracy_text, (20, 0))

            pygame.display.flip()
            pygame.display.update()