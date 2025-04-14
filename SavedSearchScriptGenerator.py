import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

class NetSuiteFormatter:
    def __init__(self, root):
        self.root = root
        self.root.title("NetSuite Script Formatter")
        self.root.geometry("800x700")
        
        # Create the main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Script input
        ttk.Label(main_frame, text="Paste NetSuite Saved Search Script:").pack(anchor=tk.W, pady=(10, 5))
        self.script_input = scrolledtext.ScrolledText(main_frame, width=80, height=15)
        self.script_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Name input
        ttk.Label(main_frame, text="Search Name:").pack(anchor=tk.W, pady=(5, 0))
        self.name_input = ttk.Entry(main_frame, width=80)
        self.name_input.pack(fill=tk.X, pady=(0, 10))
        
        # ID input with prefix
        ttk.Label(main_frame, text="Search ID (will be prefixed with 'customsearch'):").pack(anchor=tk.W, pady=(5, 0))
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(id_frame, text="customsearch").pack(side=tk.LEFT)
        self.id_input = ttk.Entry(id_frame, width=76)
        self.id_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Description input
        ttk.Label(main_frame, text="Description:").pack(anchor=tk.W, pady=(5, 0))
        self.description_input = scrolledtext.ScrolledText(main_frame, width=80, height=5)
        self.description_input.pack(fill=tk.BOTH, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Process and Save", command=self.process_and_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Preview", command=self.preview).pack(side=tk.RIGHT, padx=5)
    
    def clear_form(self):
        self.script_input.delete('1.0', tk.END)
        self.name_input.delete(0, tk.END)
        self.id_input.delete(0, tk.END)
        self.description_input.delete('1.0', tk.END)
    
    def format_script(self):
        # Get inputs
        script = self.script_input.get('1.0', tk.END).strip()
        name = self.name_input.get().strip()
        id_suffix = self.id_input.get().strip()
        description = self.description_input.get('1.0', tk.END).strip()
        
        # Validate inputs
        if not script or not name or not id_suffix or not description:
            raise ValueError("All fields are required")
        
        search_id = "customsearch" + id_suffix
        
        # Format description as comments
        formatted_description = "      // Description:\n"
        for line in description.split('\n'):
            formatted_description += "      // " + line + "\n"
        
        # Extract the variable name directly
        start_idx = script.find("var ")
        end_idx = script.find(" = search.create")
        if start_idx == -1 or end_idx == -1:
            raise ValueError("Could not find search variable in script")
        
        search_var = script[start_idx + 4:end_idx].strip()
        
        # Find the searchResultCount section to remove
        count_start_idx = script.find("var searchResultCount")
        run_each_idx = script.find(".run().each")
        comment_idx = script.find("/*")
        
        # Extract the search.create section
        if count_start_idx == -1 or run_each_idx == -1:
            search_create_code = script[start_idx:comment_idx].strip()
        else:
            search_create_code = script[start_idx:count_start_idx].strip()
        
        # Build the final script
        result = "require(['N/search'], function(search) {\n"
        result += "   try {\n"
        result += " \n"
        result += formatted_description + "\n"
        result += "      " + search_create_code + "\n"
        result += "      " + search_var + ".id=\"" + search_id + "\";\n"
        result += "      " + search_var + ".title=\"" + name + "\";\n"
        result += "      var newSearchId = " + search_var + ".save();\n"
        result += " \n"
        result += "      console.log('Search recreated successfully');\n"
        result += " \n"
        result += "   } catch (e) {\n"
        result += "      console.error(e.message);\n"
        result += "   }\n"
        result += "})"
        
        return result
    
    def preview(self):
        try:
            formatted_script = self.format_script()
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Script Preview")
            preview_window.geometry("800x600")
            
            preview_text = scrolledtext.ScrolledText(preview_window, width=80, height=30)
            preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            preview_text.insert(tk.END, formatted_script)
            preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def process_and_save(self):
        try:
            formatted_script = self.format_script()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".js",
                filetypes=[("JavaScript files", "*.js"), ("All files", "*.*")],
                initialfile=self.name_input.get().replace(' ', '_') + ".js"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(formatted_script)
                messagebox.showinfo("Success", "Script saved successfully to:\n" + file_path)
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = NetSuiteFormatter(root)
    root.mainloop()