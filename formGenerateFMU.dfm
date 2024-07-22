object Form1: TForm1
  Left = 0
  Top = 0
  Caption = 'FMU Generator'
  ClientHeight = 276
  ClientWidth = 288
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
    Width = 288
    Height = 276
    Align = alClient
    TabOrder = 0
    object listFiles: TListBox
      Left = 1
      Top = 1
      Width = 286
      Height = 167
      Align = alClient
      ItemHeight = 13
      TabOrder = 0
    end
    object Panel2: TPanel
      Left = 1
      Top = 168
      Width = 286
      Height = 107
      Align = alBottom
      TabOrder = 1
      object btnGenerateFMU: TButton
        Left = 8
        Top = 44
        Width = 89
        Height = 29
        Caption = 'Generate FMU'
        TabOrder = 0
        OnClick = btnGenerateFMUClick
      end
      object btnAddFiles: TButton
        Left = 8
        Top = 6
        Width = 89
        Height = 28
        Caption = 'Add File'
        TabOrder = 1
        OnClick = btnAddFilesClick
      end
      object rgpVersion: TRadioGroup
        Left = 112
        Top = 6
        Width = 93
        Height = 93
        ItemIndex = 3
        Items.Strings = (
          'Python 2.7'
          'Python 3.8'
          'Python 3.9'
          'Python 3.11'
          'Python 3.12')
        TabOrder = 2
        OnClick = rgpVersionClick
      end
      object rgpPlataform: TRadioGroup
        Left = 212
        Top = 6
        Width = 67
        Height = 93
        ItemIndex = 1
        Items.Strings = (
          'x86'
          'x64')
        TabOrder = 3
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
    Left = 104
    Top = 200
  end
end
