object Form1: TForm1
  Left = 0
  Top = 0
  Caption = 'FMU Generator'
  ClientHeight = 277
  ClientWidth = 288
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 288
    Height = 277
    Align = alClient
    TabOrder = 0
    object listFiles: TListBox
      Left = 1
      Top = 1
      Width = 286
      Height = 193
      Align = alClient
      ItemHeight = 13
      TabOrder = 0
    end
    object Panel2: TPanel
      Left = 1
      Top = 194
      Width = 286
      Height = 82
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
        Left = 160
        Top = 6
        Width = 112
        Height = 67
        ItemIndex = 1
        Items.Strings = (
          'Python 2.7'
          'Python 3.8')
        TabOrder = 2
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
    Left = 120
    Top = 224
  end
end
