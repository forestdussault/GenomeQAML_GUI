import os
import glob
import subprocess
import tkinter as tk
import tkinter.ttk
from tkinter import filedialog
from tkinter import messagebox


class Window(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        # Grid
        self.grid()

        # Title
        self.master.title('GenomeQAML')

        # Progress bar
        self.progress = tkinter.ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress_bar = tk.Button(self, text='', command=self.bar)

        # full space of root window
        self.pack(fill=tk.BOTH, expand=1)

        # create a quit button instance
        self.quitButton = tk.Button(self, text='Quit', command=self.client_exit)

        # input folder browser button
        self.inFolderBrowserButton = tk.Button(self, text='Select Directory', command=self.inDirectoryBox)

        # output folder browser button
        self.outFolderBrowserButton = tk.Button(self, text='Select Output Folder', command=self.outDirectoryBox)

        # submit job button
        self.submitButton = tk.Button(self, text='Run GenomeQAML', command=self.runQaml)

        # Browser text box
        self.inFolderTextBox = tk.Entry(self)
        self.inFolderTextBox.update()
        self.inFolderTextBox.focus_set()

        # Output text box
        self.outFolderTextBox = tk.Entry(self)
        self.outFolderTextBox.update()
        self.outFolderTextBox.focus_set()

        # genomeQAML output box
        self.outputBox = tk.Text(self)
        self.outputBox.update()

        ### INPUT FOLDER
        # place folder browser button
        self.inFolderBrowserButton.grid(column=0, row=1, sticky='NSEW')

        # place browser text box
        self.inFolderTextBox.grid(column=2, row=1, sticky='NSEW')

        ### OUTPUT FOLDER
        # place folder browser button
        self.outFolderBrowserButton.grid(column=0, row=2, sticky='NSEW')

        # place browser text box
        self.outFolderTextBox.grid(column=2, row=2, sticky='NSEW')

        ### RUN GENOMEQAML
        # place runQamlButton
        self.submitButton.grid(column=0, row=3, sticky='NSEW')

        ### GENOMEQAML OUTPUT
        # place output box
        self.outputBox.grid(column=2, row=3, sticky='NSEW')

        ### PROGRESSBAR
        # place progress bar
        self.progress.grid(column=2, row=5, sticky='NSEW')

        ### QUIT
        # place quitButton
        self.quitButton.grid(column=0, row=5, sticky='NSEW')



    def client_exit(self):
        exit()


    def inDirectoryBox(self, title=None, dirName=None):
        options = {}
        options['initialdir'] = dirName
        options['title'] = title
        options['mustexist'] = True
        self.inDirName = filedialog.askdirectory(**options)
        if self.inDirName == "":
            return None
        else:
            self.inFolderTextBox.insert(index=0, string=str(self.inDirName))
            return self.inDirName

    def outDirectoryBox(self, title=None, dirName=None):
        options = {}
        options['initialdir'] = dirName
        options['title'] = title
        options['mustexist'] = False
        self.outDirName = filedialog.askdirectory(**options)
        if self.outDirName == "":
            return None
        else:
            self.outFolderTextBox.insert(index=0, string=str(self.outDirName))
            return self.outDirName

    def runQaml(self):
        # Make sure FASTA files are available
        valid_in = self.validate_fasta_folder()
        valid_out = self.validate_is_folder()
        if not valid_in:
            tk.messagebox.showinfo("Error", "No FASTA files detected in folder. Please specify a new folder.")
        elif not valid_out:
            tk.messagebox.showinfo("Error", "Invalid entry for Output Folder. Please specify a new folder.")
        else:
            # Clear box
            self.outputBox.delete('1.0', tk.END)

            # Initial  message
            self.outputBox.insert(tk.END, 'Running GenomeQAML on {}\n\n'.format(self.inFolderTextBox.get()))

            # Command (-r to specify output location)
            cmd = 'classify.py -t {} -r {}'.format(self.inFolderTextBox.get(),
                                                   os.path.join(self.outFolderTextBox.get(),
                                                                os.path.basename(self.inFolderTextBox.get())+'_output.csv'))

            # Show raw command
            # self.outputBox.insert(tk.END, cmd)
            # self.outputBox.insert(tk.END, '\n\n')

            # Run command
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash')
            line_num = 0
            for line in p.stdout:
                line_num += 1
                # output = str(line.decode('UTF-8'))
                # self.outputBox.insert(tk.END, output)

                # Temporary workaround for prettier text output
                if line_num == 2:
                    self.outputBox.insert(tk.END, 'Using MASH to determine genera of samples...\n')
                elif line_num ==3:
                    self.outputBox.insert(tk.END, 'Collecting basic quality metrics...\n')
                elif line_num == 4:
                    self.outputBox.insert(tk.END, 'Using prodigal to calculate number of ORFs in each sample...\n')
                elif line_num == 5:
                    self.outputBox.insert(tk.END, 'Done! Results can be found in {}\n'.format(
                        self.outFolderTextBox.get()))

                # Progress bar update
                self.update_idletasks()
                self.progress['value'] += 33
            self.progress['value'] = 100
            self.move_extracted_features()
            self.outputBox.insert(tk.END, '\n\n===== COMPLETE =====')



    def validate_fasta_folder(self):
        folder_contents = glob.glob(self.inFolderTextBox.get())
        status = False
        for file in folder_contents:
            if 'fasta' or 'fna' or 'fa' in file:
                status = True
        return status


    def validate_is_folder(self):
        is_folder = os.path.isdir(self.outFolderTextBox.get())
        return is_folder

    def bar(self):
        self.progress['value'] = 0

    def move_extracted_features(self):
        file = glob.glob(os.path.join(self.inFolderTextBox.get(), 'extracted_features.csv'))[0]
        new_filename = file.replace('extracted_features',
                                    os.path.basename(self.inFolderTextBox.get())+'_extracted_features')
        os.rename(os.path.join(self.inFolderTextBox.get(), file),
                  os.path.join(self.outFolderTextBox.get(), os.path.basename(new_filename)))


def run():
    # Instantiate
    root = tk.Tk()

    # Size of window
    root.geometry("740x350")

    # Start
    app = Window(root)
    root.mainloop()


if __name__ == "__main__":
    run()
