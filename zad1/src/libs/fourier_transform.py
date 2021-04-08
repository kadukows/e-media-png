import cv2
import numpy as np
import matplotlib.pyplot as plt

def png_fft(filename):
    plt.figure(1)
    img=cv2.imread(filename, 0)

    fourier = np.fft.fft2(img) 
    fourier_shifted = np.fft.fftshift(fourier) 
    
    fourier_magnitude = np.asarray(20*np.log10(np.abs(fourier_shifted)) ,dtype=np.uint8) 
    fourier_phase = np.asarray(np.angle(fourier_shifted),dtype=np.uint8)

    plt.subplot(131),plt.imshow(img, cmap = 'gray')  
    plt.title('Original image'), plt.xticks([]), plt.yticks([])
        
    plt.subplot(132),plt.imshow(fourier_magnitude, cmap = 'gray')
    plt.title('FFT Magnitude'), plt.xticks([]), plt.yticks([])
        
    plt.subplot(133),plt.imshow(fourier_phase, cmap = 'gray')
    plt.title('FFT Phase'), plt.xticks([]), plt.yticks([])

    plt.show()


def check_png_fft(filename):
    plt.figure(2)  
    
    img=cv2.imread(filename, 0)
    fourier = np.fft.fft2(img)
    fourier_inverted=np.fft.ifft2(fourier)

    plt.subplot(121),plt.imshow(img, cmap = 'gray') 
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    
    plt.subplot(122),plt.imshow( np.asarray(fourier_inverted, dtype=np.uint8), cmap = 'gray')
    plt.title('Image after FFT and inverse FFT'), plt.xticks([]), plt.yticks([])
    
    plt.show()