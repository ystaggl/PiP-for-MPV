SystemCursor(OnOff=1)   ; INIT = "I","Init"; OFF = 0,"Off"; TOGGLE = -1,"T","Toggle"; ON = others
{
    static AndMask, XorMask, $, h_cursor
        ,c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13 ; system cursors
        , b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12,b13   ; blank cursors
        , h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13   ; handles of default cursors
    if (OnOff = "Init" or OnOff = "I" or $ = "")       ; init when requested or at first call
    {
        $ = h                                          ; active default cursors
        VarSetCapacity( h_cursor,4444, 1 )
        VarSetCapacity( AndMask, 32*4, 0xFF )
        VarSetCapacity( XorMask, 32*4, 0 )
        system_cursors = 32512,32513,32514,32515,32516,32642,32643,32644,32645,32646,32648,32649,32650
        StringSplit c, system_cursors, `,
        Loop %c0%
        {
            h_cursor   := DllCall( "LoadCursor", "Ptr",0, "Ptr",c%A_Index% )
            h%A_Index% := DllCall( "CopyImage", "Ptr",h_cursor, "UInt",2, "Int",0, "Int",0, "UInt",0 )
            b%A_Index% := DllCall( "CreateCursor", "Ptr",0, "Int",0, "Int",0
                , "Int",32, "Int",32, "Ptr",&AndMask, "Ptr",&XorMask )
        }
    }
    if (OnOff = 0 or OnOff = "Off" or $ = "h" and (OnOff < 0 or OnOff = "Toggle" or OnOff = "T"))
        $ = b  ; use blank cursors
    else
        $ = h  ; use the saved cursors

    Loop %c0%
    {
        h_cursor := DllCall( "CopyImage", "Ptr",%$%%A_Index%, "UInt",2, "Int",0, "Int",0, "UInt",0 )
        DllCall( "SetSystemCursor", "Ptr",h_cursor, "UInt",c%A_Index% )
    }
}
#If GetKeyState("ScrollLock","T")

F1::
WinGetActiveTitle, LastWin
Winset, AlwaysOnTop, On, ahk_class mpv
Winset, Style, -0x800000, ahk_class mpv
Winset, Style, -0x400000, ahk_class mpv
Winset, Style, -0x80000, ahk_class mpv
Winset, Style, -0x40000, ahk_class mpv
Winset, Redraw,, ahk_class mpv
WinMove, ahk_class mpv,, 1310, 594, 565, 323 
WinActivate, %LastWin%
ThickFrame := 0
Transparent := 0
return

F2::
Switch ThickFrame
{
Case 0:
	WinGetActiveTitle, LastWin
	Winset, Style, +0x40000, ahk_class mpv
	ThickFrame := 1
Case 1:
	Winset, Style, -0x40000, ahk_class mpv
	ThickFrame := 0
	WinActivate, %LastWin%
default:
	ThickFrame := 1
}

return

F3::
Winset, AlwaysOnTop, Off, ahk_class mpv
Winset, Style, +0x800000, ahk_class mpv
Winset, Style, +0x400000, ahk_class mpv
Winset, Style, +0x80000, ahk_class mpv
Winset, Style, +0x40000, ahk_class mpv
Winset, Redraw,, ahk_class mpv
WinMove, ahk_class mpv,,312,125,1296,759
return

F4::
Switch Transparent
{
Case 0:
	WinSet, Transparent, 120, ahk_class mpv
	Transparent := 1
Case 1:
	WinSet, Transparent, Off, ahk_class mpv
	Transparent := 0
default:
	Transparent := 1
}
return

F5::
SystemCursor(T)
return


F6::
WinShow, ahk_class TaigaMainW
ControlSend, ahk_parent, ^n, Taiga
WinWait, ahk_class mpv
WinHide, ahk_class TaigaMainW
return

F7::
if KeepWinZRunning  ; This means an underlying thread is already running the loop below.
{
    KeepWinZRunning := false  ; Signal that thread's loop to stop.
    return  ; End this thread so that the one underneath will resume and see the change made by the line above.
}
; Otherwise:
KeepWinZRunning := true
Loop
{
    ; The next four lines are the action you want to repeat (update them to suit your preferences):
	WinWaitClose, ahk_class mpv
	ControlSend, ahk_parent, ^n, Taiga
	WinWait, ahk_class mpv
	WinGetActiveTitle, LastWin
	WinActivate, ahk_class mpv
	Winset, AlwaysOnTop, On, ahk_class mpv
	Winset, Style, -0x800000, ahk_class mpv
	Winset, Style, -0x400000, ahk_class mpv
	Winset, Style, -0x80000, ahk_class mpv
	Winset, Style, -0x40000, ahk_class mpv
	Winset, Redraw,, ahk_class mpv
	WinMove, ahk_class mpv,, 1356, 691, 520, 298 
	WinActivate, %LastWin%
	ThickFrame := 0
	Transparent := 0
    ; But leave the rest below unchanged.
    if not KeepWinZRunning  ; The user signaled the loop to stop by pressing Win-Z again.
        break  ; Break out of this loop.
}
KeepWinZRunning := false  ; Reset in preparation for the next press of this hotkey.
return

F8::
Switch HideTaiga
{
Case 0:
	WinShow, ahk_class TaigaMainW
	HideTaiga := 1
Case 1:
	WinHide, ahk_class TaigaMainW
	HideTaiga := 0
default:
	HideTaiga := 1
} 
return
