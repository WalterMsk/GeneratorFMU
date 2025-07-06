//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "formGenerateFMU.h"
#include <string>
#include <dir.h>
#include <dirent.h>

#pragma link "Vcl.FileCtrl"
#include <Vcl.FileCtrl.hpp>  // Tenta incluir, pode n�o existir

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
    if (level > 0 && !rmdir(path.c_str()))// o diret�rio raiz nao � apagado
		return false; // delete the directory
    return true;
}
//------------------------------------------------------------------------------


std::wstring ExePath() {
	TCHAR buffer[MAX_PATH] = { 0 };
	GetModuleFileName( NULL, buffer, MAX_PATH );
	std::wstring::size_type pos = std::wstring(buffer).find_last_of(L"\\/");
	return std::wstring(buffer).substr(0, pos);
}
//------------------------------------------------------------------------------

bool IsFolder(const UnicodeString &path)
{
	return TDirectory::Exists(path);
}
//------------------------------------------------------------------------------

// Fun��o recursiva que percorre pasta e arquivos
void ProcessFolderRecursively(const UnicodeString &folder, const UnicodeString &base = L"")
{
    UnicodeString relativePath = base.IsEmpty() ? ExtractFileName(folder) : base + L"\\" + ExtractFileName(folder);
	// Primeiro, processa subpastas
	for (auto& dir : TDirectory::GetDirectories(folder))
	{
		ProcessFolderRecursively(dir, relativePath);
	}

	// Agora, processa arquivos
	for (auto& file : TDirectory::GetFiles(folder))
	{
		UnicodeString fileName = ExtractFileName(file);
		UnicodeString folderPath = UnicodeString("temp\\sources\\") + relativePath;
		UnicodeString fullPath = folderPath + L"\\" + fileName;
		TDirectory::CreateDirectory(folderPath);
		CopyFileW(file.c_str(), fullPath.c_str(), false);
	}
}
//------------------------------------------------------------------------------

void TForm1::CreateTempFolder()
{
	if (DirectoryExists("temp"))
		LimpaDirSub("temp");
	else
		//Creating temporary folder
		if (mkdir("temp") != 0) {
			char* erro = new char[200];
			sprintf(erro,"Oh dear, something went wrong with mkdir()! %s - %d\n", strerror(errno),_clearfp());
			ShowMessage(erro);
			return;
		}

	//binaries
	mkdir("temp\\binaries");
	//documentation
	mkdir("temp\\documentation");
	//sources
	mkdir("temp\\sources");

	std::string version;
	if (rgpVersion->ItemIndex == 1)
		version = "python38";
	else  if (rgpVersion->ItemIndex == 2)
		version = "python39";
	else  if (rgpVersion->ItemIndex == 3)
		version = "python311";
	else  if (rgpVersion->ItemIndex == 4)
		version = "python312";
	else
		version = "python27";

	std::string platform;
	std::string libFile;
	if (rgpPlataform->ItemIndex == 1) {
		platform = "win64";
		libFile = ".a";
	} else {
		platform = "win32";
		libFile = ".lib";
	}
	// source winXX
	mkdir(std::string("temp\\binaries\\" + platform).c_str());

	for (int i = 0; i < listFiles->Items->Count; i++) {
		std::string file = AnsiString(listFiles->Items->Strings[i]).c_str();
		std::string fileName = AnsiString(ExtractFileName(listFiles->Items->Strings[i])).c_str();
		std::string fileExt = AnsiString(ExtractFileExt(listFiles->Items->Strings[i])).c_str();
		if (fileExt == ".xml")
			CopyFileA(file.c_str(),std::string("temp\\" + fileName).c_str(), false);
		if (fileExt == ".dll")
			CopyFileA(file.c_str(),std::string("temp\\binaries\\" + platform + "\\" + fileName).c_str(), false);
		if ((fileExt == ".py") || (fileExt == ".c") || (fileExt == ".cpp") || (fileExt == ".h") || (fileExt == ".idf"))
			CopyFileA(file.c_str(),std::string("temp\\sources\\" + fileName).c_str(), false);
		if ((fileExt == ".png") || (fileExt == ".html"))
			CopyFileA(file.c_str(),std::string("temp\\documentation\\" + fileName).c_str(), false);
		if (IsFolder(UnicodeString(file.c_str()))) {
			ProcessFolderRecursively(UnicodeString(file.c_str()));
		}
		if (fileExt == "") {
			CopyFileA(file.c_str(),std::string("temp\\sources\\" + fileName).c_str(), false);
		}
	}

	std::string fileOrigin = version + "\\" + platform + "\\PythonModel.dll";
	CopyFileA(fileOrigin.c_str(),std::string("temp\\binaries\\" + platform + "\\PythonModel.dll").c_str(), false);
	fileOrigin = version + "\\" + platform + "\\" + version + ".dll";
	CopyFileA(fileOrigin.c_str(),std::string("temp\\binaries\\" + platform + "\\" + version + ".dll").c_str(), false);
	fileOrigin = version + "\\" + platform + "\\" + version + libFile;
	CopyFileA(fileOrigin.c_str(),std::string("temp\\binaries\\" + platform + "\\" + version + libFile).c_str(), false);
}
//---------------------------------------------------------------------------


void __fastcall TForm1::rgpVersionClick(TObject *Sender)
{
	if (((TRadioGroup*)Sender)->ItemIndex == 0) {
		rgpPlataform->ItemIndex = 0;
		rgpPlataform->Enabled = false;
	} else {
		rgpPlataform->Enabled = true;
    }
}
//---------------------------------------------------------------------------


void __fastcall TForm1::btnAddFolderClick(TObject *Sender)
{
	UnicodeString folder = "C:\\";
	if (SelectDirectory("Selecione uma pasta", "", folder)) {
		listFiles->Items->Add(folder);
	}
}
//---------------------------------------------------------------------------

