//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "formGenerateFMU.h"
#include <string>
#include <dir.h>
#include <dirent.h>
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TForm1 *Form1;
//---------------------------------------------------------------------------
__fastcall TForm1::TForm1(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TForm1::btnGenerateFMUClick(TObject *Sender)
{
	CreateTempFolder();
	
	std::string fileName;
	if (SaveDialog1->Execute()) {
		fileName = AnsiString(SaveDialog1->FileName).c_str();

		TZipFile* zip = new TZipFile();
		zip->ZipDirectoryContents(fileName.c_str(),"temp");
		zip->Close();
		if (FileExists(fileName.c_str()))
			ShowMessage("FMU file successfull created.");
    }
}
//---------------------------------------------------------------------------
void __fastcall TForm1::btnAddFilesClick(TObject *Sender)
{
	if (OpenDialog1->Execute()) {
		for (int i = 0; i < OpenDialog1->Files->Count; i++) {
			listFiles->Items->Add(OpenDialog1->Files->Strings[i]);
		}
	}
}
//---------------------------------------------------------------------------


//
bool TForm1::LimpaDirSub(std::string path, int level)
{
    if (path[path.length()-1] != '\\')
        path += "\\";
    // first off, we need to create a pointer to a directory
    DIR *pdir = 0;
    pdir = opendir (path.c_str());
    struct dirent* pent = NULL;
    if (pdir == NULL) { // if pdir wasn't initialised correctly
        return false; // return false to say "we couldn't do it"
    } // end if
    char file[256];

    int counter = 1; // use this to skip the first TWO which cause an infinite
                     // loop (and eventually, stack overflow)
	while ((pent = readdir (pdir))) {// while there is still some in dir. to list
        if (counter > 2) {
            for (unsigned i = 0; i < 256; i++)
                file[i] = '\0';
            strcat(file, path.c_str());
            if (pent == NULL) { // if pent has not been initialised correctly
                return false; // we couldn't do it
            } //otherwise it was initialised correctly, so let's delete the file

            // concatenate the strings to get the complete path
			strcat(file, pent->d_name);
			if (DirectoryExists(file) == true) {
                LimpaDirSub(file,level+1);
            } else { // it's a file, we can use remove
                remove(file);
            }
        } counter++;
    }

    // finally, let's clean up
    closedir (pdir); // close the directory
    if (level > 0 && !rmdir(path.c_str()))// o diretório raiz nao é apagado
        return false; // delete the directory
    return true;
}
//------------------------------------------------------------------------------


void TForm1::CreateTempFolder()
{
	if (DirectoryExists("temp"))
		LimpaDirSub("temp");
	//Creating temporary folder
	MkDir("temp");
	//binaries
	MkDir("temp\\binaries");
	//documentation
	MkDir("temp\\documentation");
	//sources
	MkDir("temp\\sources");
	//sources win32
 	MkDir("temp\\binaries\\win32");

	for (int i = 0; i < listFiles->Items->Count; i++) {
		std::string file = AnsiString(listFiles->Items->Strings[i]).c_str();
		std::string fileName = AnsiString(ExtractFileName(listFiles->Items->Strings[i])).c_str();
		std::string fileExt = AnsiString(ExtractFileExt(listFiles->Items->Strings[i])).c_str();
		if (fileExt == ".xml")
			CopyFileA(file.c_str(),std::string("temp\\" + fileName).c_str(), false);
		if (fileExt == ".dll")
			CopyFileA(file.c_str(),std::string("temp\\binaries\\win32\\" + fileName).c_str(), false);
		if ((fileExt == ".py") || (fileExt == ".c") || (fileExt == ".cpp") || (fileExt == ".h") || (fileExt == ".idf"))
			CopyFileA(file.c_str(),std::string("temp\\sources\\" + fileName).c_str(), false);
		if ((fileExt == ".png") || (fileExt == ".html"))
			CopyFileA(file.c_str(),std::string("temp\\documentation\\" + fileName).c_str(), false);
	}

	std::string version;
	if (rgpVersion->ItemIndex == 1)
		version = "python38";
	else
		version = "python27";
	std::string fileOrigin = version + "\\bin\\PythonModel.dll";
	CopyFileA(fileOrigin.c_str(),std::string("temp\\binaries\\win32\\PythonModel.dll").c_str(), false);
	fileOrigin = version + "\\bin\\" + version + ".dll";
	CopyFileA(fileOrigin.c_str(),std::string("temp\\binaries\\win32\\" + version + ".dll").c_str(), false);
	fileOrigin = version + "\\bin\\" + version +"_xe.lib";
	CopyFileA(fileOrigin.c_str(),std::string("temp\\binaries\\win32\\" + version +"_xe.lib").c_str(), false);
}
//---------------------------------------------------------------------------

