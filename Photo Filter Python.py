import cv2
import numpy as np
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

#Общие переменные 
original_image = None
current_image = None
update_timer = None
pending_brightness = None
pending_contrast = None
current_brightness = 0
current_contrast = 1.0
pending_shadows = None
current_shadows = 0
brightness_var = None
contrast_var = None
shadows_var = None
pending_exposure = None
pending_warmth = None
current_exposure = 1.0
current_warmth = 0
active_filter = None

# Приветствие
messagebox.showinfo("Hi!", "This is my first project!")

def text_to_user():
    global original_image, current_image
    filename = filedialog.askopenfilename()
    if filename:
        print("Выбрано:", filename)
        
        # Открываем картинку
        original_image = Image.open(filename)
        current_image = original_image.copy()  # копируем для изменений
        
        # Показываем
        show_current_image()

def show_main_menu():
    """Показывает три основные кнопки (главное меню)"""
    # Очищаем фрейм
    for widget in subcategory_frame.winfo_children():
        widget.destroy()

    # Создаём три кнопки в ряд
    btn_edit_photo = tk.Button(subcategory_frame, text="Adjust", width=15, command=show_adjust_options)
    btn_edit_photo.pack(side='left', padx=15)

    btn_filter = tk.Button(subcategory_frame, text="Filter", width=15, command=show_filters_options)
    btn_filter.pack(side='left', padx=5)

    btn_geometry = tk.Button(subcategory_frame, text="Geometry", width=15,command=show_geometry_options)
    btn_geometry.pack(side='left', padx=5)
    
    # Запоминаем, что мы на Уровне 1
    global current_level
    current_level = 1
    print("Main menu")

def show_edit_options():
    """Обработчик кнопки Edit — переключает между Уровнем 0 и Уровнем 1"""
    global current_level
    
    if 'current_level' not in globals() or current_level == 0:
        # Если уровень 0 или не определён — показываем меню
        show_main_menu()
    else:
        # Если мы на любом другом уровне — скрываем всё (возврат на уровень 0)
        for widget in subcategory_frame.winfo_children():
            widget.destroy()
        current_level = 0

def apply_changes():
    """Принудительно применяет все настройки"""
    global current_image
    if original_image is None:
        return
    
    print("Apply pressed — applying all adjustments")
    apply_all_adjustments()  

def discard_changes():
    """Сбрасывает все настройки к исходным значениям"""
    global current_brightness, current_contrast, current_shadows,current_exposure,current_warmth 
    global pending_brightness, pending_contrast, pending_shadows, pending_exposure,pending_warmth
    global brightness_var, contrast_var, shadows_var, exposure_var, warmth_var
    global current_image, original_image
    
    
    if original_image is None:
        return
    
    # Сбрасываем переменные настроек
    current_brightness = 0
    current_contrast = 1.0
    current_shadows = 0
    current_exposure = 1.0
    current_warmth = 0
    active_filter.set("none")
    # Сбрасываем pending значения
    pending_brightness = None
    pending_contrast = None
    pending_shadows = None
    pending_exposure = None
    pending_warmth = None
    # СБРАСЫВАЕМ ПОЛЗУНКИ ЧЕРЕЗ ИХ ПЕРЕМЕННЫЕ
    if brightness_var is not None:
        brightness_var.set(0)
    if contrast_var is not None:
        contrast_var.set(0)
    if shadows_var is not None:
        shadows_var.set(0)
    if exposure_var is not None:
        exposure_var.set(0)
    if warmth_var is not None:
        warmth_var.set(0)
    
    apply_all_adjustments()
    # Возвращаемся к оригинальному изображению
    current_image = original_image.copy()
    show_current_image()
    
    print("All changes discarded")

def on_left(scale_widget):
    scale_widget.set(scale_widget.get() - 1)

def on_right(scale_widget):
    scale_widget.set(scale_widget.get() + 1)

def show_adjust_options():
    #Показывает ползунки яркости, контраста, теней, экспозиции, теплоты
    global current_level, brightness_var, contrast_var, shadows_var, exposure_var, warmth_var
    global original_image, current_image
    
    # Очищаем фрейм с подкатегориями
    for widget in subcategory_frame.winfo_children():
        widget.destroy()
    
    # Настройки для цикла
    settings = [
        ("Brightness", "brightness_var", "brightness", -100, 100),
        ("Contrast", "contrast_var", "contrast", -100, 100),
        ("Shadows", "shadows_var", "shadows", -100, 100),
        ("Exposure", "exposure_var", "exposure", -100, 100),
        ("Warmth", "warmth_var", "warmth", -100, 100)
    ]
    
    for name, var_name, setting_key, from_val, to_val in settings:
        # Заголовок
        label = tk.Label(subcategory_frame, text=name, bg='lightblue')
        label.pack(pady=(10, 0))
        
        # Создаём переменную для ползунка
        var = tk.IntVar()
        var.set(0)
        globals()[var_name] = var
        
        # Ползунок
        scale = tk.Scale(
            subcategory_frame,
            from_=from_val,
            to=to_val,
            orient='horizontal',
            variable=var,
            command=lambda v, key=setting_key: update_setting(key, v)
        )
        scale.pack(pady=(0, 10), padx=20, fill='x')
    
        scale.bind("<Left>", lambda e, s=scale: on_left(s))
        scale.bind("<Right>", lambda e, s=scale: on_right(s))

    # Кнопка "Назад" в главное меню
    btn_back = tk.Button(subcategory_frame, text="← Back", command=show_main_menu)
    btn_back.pack(pady=10)

    # Панель для кнопок
    button_panel = tk.Frame(subcategory_frame, bg='lightblue')
    button_panel.pack(pady=10)

    btn_apply = tk.Button(button_panel, text="Apply", command=apply_changes, width=10)
    btn_apply.pack(side='right', padx=35)

    btn_discard = tk.Button(button_panel, text="Discard", command=discard_changes, width=10)
    btn_discard.pack(side='left', padx=35)
    
    current_level = 2
    print("Adjust settings was showed")


def analyze_image():
    print("Start")

def update_setting(setting_name, value):
    """Универсальная функция для обновления настроек"""
    config = {
        'brightness': {
            'pending': 'pending_brightness',
            'transform': lambda v: int(v)
        },
        'contrast': {
            'pending': 'pending_contrast',
            'transform': lambda v: 1.0 + (int(v) / 100) * 0.5
        },
        'shadows': {
            'pending': 'pending_shadows',
            'transform': lambda v: int(v)
        },
        'exposure': {
            'pending': 'pending_exposure',
            'transform': lambda v: 1.0 + (int(v) / 100) * 0.5
        },
        'warmth': {
            'pending': 'pending_warmth',
            'transform': lambda v: int(v)
        }
    }
    
    cfg = config[setting_name]
    pending_var = cfg['pending']
    
    # Устанавливаем pending
    globals()[pending_var] = cfg['transform'](value)
    
    # Таймер
    global update_timer
    if update_timer is not None:
        update_timer.cancel()
    
    update_timer = threading.Timer(0.1, lambda: apply_setting(setting_name))
    update_timer.start()

def apply_setting(setting_name):
    """Универсальная функция для применения настроек"""
    config = {
        'brightness': {
            'pending': 'pending_brightness',
            'current': 'current_brightness'
        },
        'contrast': {
            'pending': 'pending_contrast',
            'current': 'current_contrast'
        },
        'shadows': {
            'pending': 'pending_shadows',
            'current': 'current_shadows'
        },
        'exposure': {
            'pending': 'pending_exposure',
            'current': 'current_exposure'
        },
        'warmth': {
            'pending': 'pending_warmth',
            'current': 'current_warmth'
        }
    }
    
    cfg = config[setting_name]
    pending_var = cfg['pending']
    current_var = cfg['current']
    
    pending_value = globals()[pending_var]
    if pending_value is None:
        return
    
    globals()[current_var] = pending_value
    apply_all_adjustments()

def apply_all_adjustments():
    #Применяем текущие настройки к оригиналу
    global original_image, current_image
    global current_brightness, current_contrast, current_shadows
    global current_exposure, current_warmth, active_filter
    
    if original_image is None:
        return
    
    # Начинаем с оригинала и конвертируем в формат OpenCV (BGR)
    img = original_image.copy()
    img_np = np.array(img)
    # Конвертируем RGB в BGR для OpenCV
    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    # 1. Тени (работаем с яркостным каналом)
    if current_shadows != 0:
        # Конвертируем в HSV
        hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Преобразуем v в float32 для вычислений
        v_float = v.astype(np.float32)
        
        # Создаем маску теней (яркость < 128)
        shadow_mask = v_float < 128
        
        # Применяем изменение только к теням
        v_float[shadow_mask] = v_float[shadow_mask] + current_shadows
        
        # Ограничиваем значения
        v_float = np.clip(v_float, 0, 255)
        
        # Преобразуем обратно в uint8
        v = v_float.astype(np.uint8)
        
        # Собираем обратно
        hsv = cv2.merge([h, s, v])
        img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    # 2. Экспозиция (умножение)
    if current_exposure != 1.0:
        img_np = cv2.convertScaleAbs(img_np, alpha=current_exposure, beta=0)
    
    # 3. Теплота (баланс красного/синего)
    if current_warmth != 0:
        # OpenCV хранит в порядке BGR
        b, g, r = cv2.split(img_np)
        
        # Преобразуем в float32
        r_float = r.astype(np.float32)
        b_float = b.astype(np.float32)
        
        # Коэффициент: от -100 до 100 -> от -0.5 до 0.5
        factor = current_warmth / 200.0
        
        # Увеличиваем красный, уменьшаем синий
        r_float = r_float * (1 + factor)
        b_float = b_float * (1 - factor)
        
        # Ограничиваем значения
        r_float = np.clip(r_float, 0, 255)
        b_float = np.clip(b_float, 0, 255)
        
        # Преобразуем обратно в uint8
        r = r_float.astype(np.uint8)
        b = b_float.astype(np.uint8)
        
        # Собираем обратно
        img_np = cv2.merge([b, g, r])
    
    # 4. Яркость (прибавление)
    if current_brightness != 0:
        img_np = cv2.convertScaleAbs(img_np, alpha=1, beta=current_brightness)
    
    # 5. Контраст (умножение)
    if current_contrast != 1.0:
        img_np = cv2.convertScaleAbs(img_np, alpha=current_contrast, beta=0)

    filter_value = active_filter.get()

    if filter_value == "mono":
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        gray = cv2.convertScaleAbs(gray,alpha= 1.3, beta=0)
        img_np = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    elif filter_value == "sepia":
        sep_mat = np.array([
            [0.2,0.15,0.12],
            [0.2,0.4,0.2],
            [0.12,0.32,0.8],
        ],dtype=np.float32)
        img_np = cv2.transform(img_np, sep_mat)
        img_np = np.clip(img_np, 0, 255).astype(np.uint8)


    elif filter_value == "hdr" :

        img_np = cv2.detailEnhance(img_np, sigma_s=30, sigma_r=0.01)
    
    elif filter_value == "vibrance":
        hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        s_float = s.astype(np.float32)
        factor = 1.0 + (1.0 - s_float / 255.0) * 1.5
        s_new = s_float * factor
        s_new = np.clip(s_new, 0, 255).astype(np.uint8)
        hsv_new = cv2.merge([h, s_new, v])
        img_np = cv2.cvtColor(hsv_new, cv2.COLOR_HSV2BGR)
    pass
    
    # Конвертируем обратно из BGR в RGB для PIL
    img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    
    # Превращаем обратно в PIL
    current_image = Image.fromarray(img_np)
    show_current_image()

    

def show_current_image():
    """Показывает текущую картинку в левой колонке"""
    global current_image
    if current_image is None:
        return
    
    # Получаем размер левой колонки
    left_width = left_frame.winfo_width() - 20
    left_height = left_frame.winfo_height() - 100
    
    # Копируем и масштабируем
    img_display = current_image.copy()
    img_display.thumbnail((left_width, left_height))
    
    photo = ImageTk.PhotoImage(img_display)
    image_label.config(image=photo)
    image_label.image = photo

def show_filters_options():
    global current_level, active_filter
    for widget in subcategory_frame.winfo_children():
        widget.destroy()

    filter_original = tk.Radiobutton(subcategory_frame,text="Original",variable=active_filter,
                   value="original",indicatoron=True,command=apply_all_adjustments)
    filter_original.pack(anchor='w',padx=15, pady=10)    

    filter_mono = tk.Radiobutton(subcategory_frame,text="Mono",variable=active_filter,
                   value="mono",indicatoron=True,command=apply_all_adjustments)
    filter_mono.pack(anchor='w',padx=15, pady=10)

    filter_sepia = tk.Radiobutton(subcategory_frame,text="Sepia",variable=active_filter,
                   value="sepia",indicatoron=True,command=apply_all_adjustments  )
    filter_sepia.pack(anchor='w',padx=15,pady=10)

    filter_HDR = tk.Radiobutton(subcategory_frame,text="HDR",variable=active_filter,
                   value="hdr",indicatoron=True,command=apply_all_adjustments  )
    filter_HDR.pack(anchor='w',padx=15,pady=10)

    filter_vibrance = tk.Radiobutton(subcategory_frame,text="Vibrance",variable=active_filter,
                   value="vibrance",indicatoron=True,command=apply_all_adjustments )
    filter_vibrance.pack(anchor='w',padx=15,pady=10)


    # Кнопка "Назад" в главное меню
    btn_back = tk.Button(subcategory_frame, text="← Back", command=show_main_menu)
    btn_back.pack(pady=10)
    
    # Панель для кнопок
    button_panel = tk.Frame(subcategory_frame, bg='lightblue')
    button_panel.pack(pady=10)

    btn_apply = tk.Button(button_panel, text="Apply", command=apply_changes, width=10)
    btn_apply.pack(side='right', padx=35)

    btn_discard = tk.Button(button_panel, text="Discard", command=discard_changes, width=10)
    btn_discard.pack(side='left', padx=35)


def show_geometry_options():
    global current_level
    for widget in subcategory_frame.winfo_children():
        widget.destroy()

    btn_Rotate_90 = tk.Button(subcategory_frame, text="Rotate 90 °",  width=10)
    btn_Rotate_90.pack(anchor='w',padx=15)

    btn_to_mirror = tk.Button(subcategory_frame, text="To mirror",  width=10)
    btn_to_mirror.pack(anchor='s',padx=15)

    label_rotate = tk.Label(subcategory_frame, text="Rotate", bg='lightblue')
    label_rotate.pack(pady=(10, 0))

    scale_rotate = tk.Scale(subcategory_frame, from_=-180, to=180, orient='horizontal')
    scale_rotate.pack(pady=(0, 10), padx=20, fill='x')


    # Кнопка "Назад" в главное меню
    btn_back = tk.Button(subcategory_frame, text="← Back", command=show_main_menu)
    btn_back.pack(pady=10)
    
    # Панель для кнопок
    button_panel = tk.Frame(subcategory_frame, bg='lightblue')
    button_panel.pack(pady=10)

    btn_apply = tk.Button(button_panel, text="Apply", command=apply_changes, width=10)
    btn_apply.pack(side='right', padx=35)

    btn_discard = tk.Button(button_panel, text="Discard", command=discard_changes, width=10)
    btn_discard.pack(side='left', padx=35)

def on_enter(event):
    # Позиционируем меню под кнопкой
    x = event.widget.winfo_rootx()
    y = event.widget.winfo_rooty() + event.widget.winfo_height()
    menu.post(x, y)

def on_leave(event):
    menu.unpost()

def save_as():
    global current_image
    if current_image is None:
        messagebox.showwarning("Warning", "No image to save!")
        return
    
    filename = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")])
    
    if filename:
        current_image.save(filename)
        print(f"Сохранено: {filename}")
        messagebox.showinfo("Success", "Image saved successfully!")

def open_new():
    global original_image, current_image
    filename = filedialog.askopenfilename()
    if filename:
        print("Выбрано:", filename)
        
        # Открываем картинку
        original_image = Image.open(filename)
        current_image = original_image.copy()  # копируем для изменений
        
        # Показываем
        show_current_image()

def quit_programm():
    result = messagebox.askyesno("Close programm",
        "All unsaved setting will be delete. Quit?")
    if result:
        window.quit()
        window.destroy()
# Окно ввода
window = tk.Tk()
window.title("Photo Filter")
window.geometry("1000x600")
window.update()

active_filter = tk.StringVar()
active_filter.set("none")

# Две колонки
#Левая колонка
left_frame = tk.Frame(window, width=550, height=550, bg='lightgrey')
left_frame.pack(side='left', padx=5, pady=10, fill='y')
left_frame.pack_propagate(False)
#Правая колонка
right_frame = tk.Frame(window, width=400, height=550, bg='lightblue')
right_frame.pack(side='right', padx=5, pady=10, fill='y')
right_frame.pack_propagate(False)

# В левой колонке:
# Верхняя панель с кнопками
top_panel_left = tk.Frame(left_frame, bg='lightgray')
top_panel_left.pack(fill='x', pady=5)

# Кнопка Save
btn_save = tk.Button(top_panel_left, text="Save", width=7,
                     font=('Arial', 10, 'bold'), )
btn_save.pack(side='left', padx=5)

# Кнопка Upload image
btn_load = tk.Button(top_panel_left, text="Upload image", command=text_to_user,
                     width=12, font=('Arial', 10, 'bold'))
btn_load.pack(side='left', padx=5)

# Место для картинки
image_label = tk.Label(left_frame)
image_label.pack(pady=10, fill='both', expand=True)

# В правой колонке:

# Верхняя панель с кнопками
top_panel_right = tk.Frame(right_frame, bg='lightgray')
top_panel_right.pack(fill='x', pady=5)

# Кнопка Analyze
btn_analyze_image = tk.Button(top_panel_right, text="Analyze Image", width=13,
                     bg='green', fg='black',font=('Arial', 10, 'bold'), )
btn_analyze_image.pack(side='left', padx=16)

# Кнопка Edit image
btn_edit_main = tk.Button(top_panel_right, text="Edit", command=show_edit_options,
                     width=13, bg='orange', fg='black', font=('Arial', 10, 'bold'))
btn_edit_main.pack(side='left',padx=5)




# Место для подкатегорий ( 3 кнопки)
subcategory_frame = tk.Frame(right_frame, bg='lightblue')
subcategory_frame.pack(pady=10, fill='x')


label_info = tk.Label(right_frame, text="Edit photo", bg='lightblue')
label_info.pack(pady=20)



# Выпадающее меню для кнопки Save
menu = tk.Menu(window, tearoff=0)
menu.add_command(label="Save as", command=save_as)
menu.add_command(label="Open new", command=open_new)
menu.add_command(label="Discard all", command=discard_changes)
menu.add_command(label="Quit", command=quit_programm)

# Привязываем события к кнопке Save
btn_save.bind("<Enter>", on_enter)
btn_save.bind("<Leave>", on_leave)
menu.bind("<Leave>", on_leave)

# Глобальные переменные для работы с картинкой
original_image = None  # оригинал (всегда без изменений)
current_image = None   # текущая обработанная картинка
current_level = 0 

# Запуск
window.mainloop()