object Form1: TForm1
  Left = 0
  Top = 0
  Caption = 'FMU Generator'
  ClientHeight = 314
  ClientWidth = 281
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  TextHeight = 13
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 281
    Height = 314
    Align = alClient
    TabOrder = 0
    ExplicitWidth = 288
    ExplicitHeight = 276
    object listFiles: TListBox
      Left = 1
      Top = 1
      Width = 279
      Height = 203
      Align = alClient
      ItemHeight = 13
      TabOrder = 0
      ExplicitLeft = 0
      ExplicitHeight = 191
    end
    object Panel2: TPanel
      Left = 1
      Top = 204
      Width = 279
      Height = 109
      Align = alBottom
      TabOrder = 1
      ExplicitTop = 203
      object btnGenerateFMU: TButton
        Left = 8
        Top = 71
        Width = 89
        Height = 26
        Caption = 'Generate FMU'
        TabOrder = 0
        OnClick = btnGenerateFMUClick
      end
      object btnAddFiles: TButton
        Left = 8
        Top = 12
        Width = 89
        Height = 25
        Caption = 'Add File'
        TabOrder = 1
        OnClick = btnAddFilesClick
      end
      object rgpVersion: TRadioGroup
        Left = 106
        Top = 6
        Width = 105
        Height = 91
        Caption = 'Python'
        Columns = 2
        ItemIndex = 4
        Items.Strings = (
          '2.7'
          '3.8'
          '3.9'
          '3.11'
          '3.12'
          '3.13')
        TabOrder = 2
        OnClick = rgpVersionClick
      end
      object rgpPlataform: TRadioGroup
        Left = 218
        Top = 12
        Width = 54
        Height = 85
        ItemIndex = 1
        Items.Strings = (
          'x86'
          'x64')
        TabOrder = 3
      end
      object btnAddFolder: TButton
        Left = 8
        Top = 41
        Width = 89
        Height = 26
        Caption = 'Add Folder'
        TabOrder = 4
        OnClick = btnAddFolderClick
      end
    end
  end
  object SaveDialog1: TSaveDialog
    DefaultExt = '.fmu'
    Filter = 'FMU|*.fmu'
    Left = 336
    Top = 24
  end
  object OpenDialog1: TOpenDialog
    Options = [ofHideReadOnly, ofAllowMultiSelect, ofEnableSizing]
    Left = 16
    Top = 120
  end
end
