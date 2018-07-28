//---------------------------------------------------------------------------

#ifndef formGenerateFMUH
#define formGenerateFMUH
//---------------------------------------------------------------------------
#include <System.Classes.hpp>
#include <Vcl.Controls.hpp>
#include <Vcl.StdCtrls.hpp>
#include <Vcl.Forms.hpp>
#include <System.Zip.hpp>
#include <Vcl.Dialogs.hpp>
#include <Vcl.ExtCtrls.hpp>
//---------------------------------------------------------------------------
class TForm1 : public TForm
{
__published:	// IDE-managed Components
	TSaveDialog *SaveDialog1;
	TPanel *Panel1;
	TListBox *listFiles;
	TPanel *Panel2;
	TButton *btnGenerateFMU;
	TButton *btnAddFiles;
	TOpenDialog *OpenDialog1;
	void __fastcall btnGenerateFMUClick(TObject *Sender);
	void __fastcall btnAddFilesClick(TObject *Sender);
private:	// User declarations
	void CreateTempFolder(void);
    bool LimpaDirSub(std::string path, int level=0);
public:		// User declarations
	__fastcall TForm1(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TForm1 *Form1;
//---------------------------------------------------------------------------
#endif
