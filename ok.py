import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk


class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap("folder1.ico")
        self.root.title("Explorateur de Fichiers")
        self.current_path = os.getcwd()
        self.history = []
        self.favorites = set()

        # Configuration générale de la fenêtre
        self.root.configure(bg="#f0f0f0", padx=15, pady=15)

        # Sidebar (barre latérale)
        self.sidebar_frame = tk.Frame(root, width=220, bg="#333333")
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.create_sidebar()

        # Conteneur principal
        self.main_frame = tk.Frame(root, bg="#ffffff", relief=tk.RIDGE, bd=2)
        self.main_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Barre de chemin
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.main_frame, textvariable=self.path_var, state='readonly', width=80,
                                    font=("Arial", 12))
        self.path_entry.pack(pady=10, fill=tk.X, padx=10)
        self.button_frame = tk.Frame(self.main_frame, bg="#ffffff")
        self.button_frame.pack(pady=5)
        # Bouton retour
        self.back_button = tk.Button(self.main_frame, text="⬅ Retour", font=("Arial", 10, "bold"), command=self.go_back,
                                     bg="#0078D7", fg="white", relief=tk.RAISED)
        self.back_button.pack(pady=5)

        # Bouton nouveau dossier
        self.new_folder_button = tk.Button(self.button_frame, text="📁 Nouveau Dossier", font=("Arial", 10, "bold"),
                                           command=self.create_folder, bg="#28a745", fg="white", relief=tk.RAISED)
        self.new_folder_button.pack(side=tk.LEFT, padx=5)

        # Bouton actualiser
        self.refresh_button = tk.Button(self.button_frame, text="🔄 Actualiser", font=("Arial", 10, "bold"),
                                        command=self.load_directory, bg="#17a2b8", fg="white", relief=tk.RAISED)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        # options de filtrage
        self.filter_var = tk.StringVar()
        self.filter_combobox = ttk.Combobox(self.button_frame, textvariable=self.filter_var,
                                            values=["Tous", "Images", "Texte"], state="readonly")
        self.filter_combobox.pack(side=tk.LEFT, padx=5)
        self.filter_combobox.current(0)
        self.filter_combobox.bind("<<ComboboxSelected>>", lambda e: self.load_directory())

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.button_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Bouton rechercher
        self.search_button = tk.Button(self.button_frame, text="🔍 Rechercher", command=self.search_files, bg="#ff9800",
                                       fg="white", relief=tk.RAISED)
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Zone d'affichage des fichiers
        self.canvas = tk.Canvas(self.main_frame, bg="#ffffff")
        self.scroll_y = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.files_frame = tk.Frame(self.canvas, bg="#ffffff")

        self.canvas.create_window((10, 10), window=self.files_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.files_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.load_directory()

    def create_sidebar(self):
        options = ["Recents", "Favorites", "Computer", "Tags"]
        for option in options:
            btn = tk.Button(self.sidebar_frame, text=option, font=("Arial", 12, "bold"), fg="white", bg="#444444",
                            relief=tk.FLAT, anchor="w", command=lambda o=option: self.sidebar_action(o))
            btn.pack(fill=tk.X, padx=15, pady=8)

    def sidebar_action(self, option):
        if option == "Favorites":
            self.show_favorites()

    def load_directory(self, path=None):

        if path:
            self.history.append(self.current_path)
            self.current_path = path

        self.path_var.set(self.current_path)
        for widget in self.files_frame.winfo_children():
            widget.destroy()
        file_filter = self.filter_var.get()
        search_query = self.search_var.get().lower()
        try:
            for item in os.listdir(self.current_path):
                item_path = os.path.join(self.current_path, item)
                is_folder = os.path.isdir(item_path)

                if file_filter == "Images" and not (
                        item.endswith(".png") or item.endswith(".jpg") or item.endswith(".jpeg")):
                    continue
                elif file_filter == "Texte" and not item.endswith(".txt"):
                    continue

                if search_query and search_query not in item.lower():
                    continue

                img = Image.open("folder.png" if is_folder else "file2.png")
                img = img.resize((50, 50), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)

                frame = tk.Frame(self.files_frame, bg="#ffffff", relief=tk.RIDGE, bd=1)
                frame.pack(side=tk.LEFT, padx=15, pady=15)

                label_img = tk.Label(frame, image=img, bg="#ffffff")
                label_img.image = img
                label_img.pack()

                details = os.stat(item_path)
                size = details.st_size
                creation_time = time.ctime(details.st_ctime)
                info_label = tk.Label(frame, text=f"Taille: {size} octets\nCréé: {creation_time}", font=("Arial", 8))
                info_label.pack()

                label_text = tk.Label(frame, text=item, wraplength=100, font=("Arial", 10))
                label_text.pack()
                label_text.bind("<Double-1>", lambda e, p=item_path: self.open_item(p))
                label_img.bind("<Double-1>", lambda e, p=item_path: self.open_item(p))
                label_img.bind("<Button-3>", lambda e, p=item_path: self.show_context_menu(e, p))
                label_text.bind("<Button-3>", lambda e, p=item_path: self.show_context_menu(e, p))
        except PermissionError:
            messagebox.showerror("Erreur", "Accès refusé à ce dossier.")

    def create_folder(self):
        folder_name = simpledialog.askstring("Nouveau Dossier", "Nom du dossier :")
        if folder_name:
            new_folder_path = os.path.join(self.current_path, folder_name)
            os.makedirs(new_folder_path, exist_ok=True)
            self.load_directory()

    def open_item(self, path):
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            os.startfile(path)

    def go_back(self):
        if self.history:
            last_path = self.history.pop()
            self.load_directory(last_path)

    def show_context_menu(self, event, path):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Ouvrir", command=lambda: self.open_item(path))
        menu.add_command(label="Supprimer", command=lambda: self.delete_item(path))
        menu.add_command(label="Renommer", command=lambda: self.rename_item(path))
        menu.add_command(label="Ajouter aux Favoris", command=lambda: self.add_to_favorites(path))
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()

    def delete_item(self, path):
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        self.load_directory()

    def rename_item(self, path):
        new_name = simpledialog.askstring("Renommer", "Nouveau nom :")
        if new_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            os.rename(path, new_path)
        self.load_directory()

    def add_to_favorites(self, path):
        if path in self.favorites:
            # chemin existant
            messagebox.showerror("Erreur", "Ce fichier/dossier est déjà dans les favoris.")
        else:
            self.favorites.add(path)
            messagebox.showinfo("Favoris", "Ajouté aux favoris !")

    def show_favorites(self):
        # Effacer l'affichage actuel des fichiers
        for widget in self.files_frame.winfo_children():
            widget.destroy()

        if not self.favorites:
            messagebox.showinfo("Aucun Favori", "Vous n'avez pas de favoris enregistrées.")
            return

        for path in self.favorites:
            is_folder = os.path.isdir(path)

            # gestion icône
            img = Image.open("folder.png" if is_folder else "file2.png")
            img = img.resize((50, 50), Image.LANCZOS)  # Redimensionner l'image
            img = ImageTk.PhotoImage(img)

            frame = tk.Frame(self.files_frame, bg="#ffffff", relief=tk.RIDGE, bd=1)
            frame.pack(side=tk.LEFT, padx=15, pady=15)

            label_img = tk.Label(frame, image=img, bg="#ffffff")
            label_img.image = img
            label_img.pack()

            details = os.stat(path)
            size = details.st_size
            creation_time = time.ctime(details.st_ctime)
            info_label = tk.Label(frame, text=f"Taille: {size} octets\nCréé: {creation_time}", font=("Arial", 8))
            info_label.pack()

            # Nom du fichier/dossier
            label_text = tk.Label(frame, text=os.path.basename(path), wraplength=100, font=("Arial", 10))
            label_text.pack()

            # Double clic pour ouvrir
            label_text.bind("<Double-1>", lambda e, p=path: self.open_item(p))
            label_img.bind("<Double-1>", lambda e, p=path: self.open_item(p))

            # Menu contextuel avec clic droit
            label_img.bind("<Button-3>", lambda e, p=path: self.show_context_menu(e, p))
            label_text.bind("<Button-3>", lambda e, p=path: self.show_context_menu(e, p))

    def search_files(self):
        self.load_directory()


if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()