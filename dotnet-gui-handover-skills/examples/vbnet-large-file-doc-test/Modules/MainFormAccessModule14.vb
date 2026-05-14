Imports System
Imports System.Configuration
Imports System.Windows.Forms

Public Module MainFormAccessModule14
    Public Function BuildForm() As MainForm
        Return New MainForm()
    End Function

    Public Function ReadFormTitle(form As MainForm) As String
        Return If(form Is Nothing, String.Empty, form.Text)
    End Function
End Module
