/*
 * ****************************************************************************
 * Copyright (c) 2013-2020, PyInstaller Development Team.
 *
 * Distributed under the terms of the GNU General Public License (version 2
 * or later) with exception for distributing the bootloader.
 *
 * The full license is in the file COPYING.txt, distributed with this software.
 *
 * SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
 * ****************************************************************************
 */

/*
 * Global shared fuctions used in many bootloader files.
 */

/*
 * Enable use of Sean's Tool Box -- public domain -- http://nothings.org/stb.h.
 * File stb.h.
 * All functions starting with 'stb_' prefix are from this toolbox.
 *
 * This define has to be only in one C source file!
 */
/* #define STB_DEFINE  1/ * * / */
/* #define STB_NO_REGISTRY 1 / * No need for Windows registry functions in stb.h. * / */

#include <stdarg.h>  /* va_list, va_start(), va_end() */
#include <stdio.h>

#ifdef _WIN32
    #include <windows.h>
    #include <direct.h>
    #include <process.h>
    #include <io.h>
#else
    #include <sys/types.h>
    #include <unistd.h>
#endif

/* On Mac OS X send debug msg also to syslog for gui app in debug mode. */
#if defined(__APPLE__) && defined(WINDOWED) && defined(LAUNCH_DEBUG)
    #include <syslog.h>
#endif

/* PyInstaller headers. */
#include "pyi_global.h"
#include "pyi_win32_utils.h"
/* Text length of MessageBox(). */
#define MBTXTLEN 1024

/* Locale is saved at the start of main(), and restored immediately before running
 * scripts in pyi_launch_run_scripts
 */
char *saved_locale;

/*
 * On Windows and with windowed mode (no console) show error messages
 * in message boxes. In windowed mode nothing is written to console.
 */

#if defined(_WIN32) && defined(WINDOWED)
void
show_message_box(const char *msg, const char *caption, UINT uType)
{
    wchar_t wmsg[MBTXTLEN];
    wchar_t wcaption[MBTXTLEN] = L"";
    if (pyi_win32_utils_from_utf8(wmsg, msg, MBTXTLEN)) {
        /* converting the caption is expected to pass since the given caption
         * is always written in US-ASCII and hard-coded, currently.
         */
        pyi_win32_utils_from_utf8(wcaption, caption, MBTXTLEN);
        MessageBoxW(NULL, wmsg, wcaption, MB_OK | uType);
    }
    else {
        /* The msg here is always shown as not human-readable string,
         * but can be the hint what the real message is.
         */
        MessageBoxA(NULL, msg, caption, MB_OK | uType);
    }
}


void
mbfatalerror(const char *fmt, ...)
{
    char msg[MBTXTLEN];
    va_list args;

    va_start(args, fmt);
    vsnprintf(msg, MBTXTLEN, fmt, args);
    va_end(args);

    show_message_box(msg, "Fatal error detected", MB_ICONEXCLAMATION);
}

void
mbothererror(const char *fmt, ...)
{
    char msg[MBTXTLEN];
    va_list args;

    va_start(args, fmt);
    vsnprintf(msg, MBTXTLEN, fmt, args);
    va_end(args);

    show_message_box(msg, "Error detected", MB_ICONWARNING);
}

    void mbfatal_winerror(const char * funcname, const char *fmt, ...)
    {
        char msg[MBTXTLEN];
        size_t size = 0;
        DWORD error_code = GetLastError();
        va_list args;

        va_start(args, fmt);
            size = vsnprintf(msg, MBTXTLEN, fmt, args);
        va_end(args);

        if(size < MBTXTLEN) {
            strncpy(msg + size, funcname, MBTXTLEN - size - 1);
            size += strlen(funcname);
        }

        if(size < MBTXTLEN) {
            strncpy(msg + size, ": ", 2);
            size += 2;
        }

        if(size < MBTXTLEN) {
            strncpy(msg + size, GetWinErrorString(error_code), MBTXTLEN - size - 1);
        }

        msg[MBTXTLEN-1] = '\0';

        show_message_box(msg, "Fatal error detected", MB_ICONEXCLAMATION);
    }

    void mbfatal_perror(const char * funcname, const char *fmt, ...)
    {
        char msg[MBTXTLEN];
        size_t size = 0;
        va_list args;

        va_start(args, fmt);
            size = vsnprintf(msg, MBTXTLEN, fmt, args);
        va_end(args);

        if(size < MBTXTLEN) {
            strncpy(msg + size, funcname, MBTXTLEN - size - 1);
            size += strlen(funcname);
        }

        if(size < MBTXTLEN) {
            strncpy(msg + size, ": ", 2);
            size += 2;
        }

        if(size < MBTXTLEN) {
            strncpy(msg + size, strerror(errno), MBTXTLEN - size - 1);
        }

        msg[MBTXTLEN-1] = '\0';

        show_message_box(msg, "Fatal error detected", MB_ICONEXCLAMATION);
    }
#endif  /* _WIN32 and WINDOWED */

/* Enable or disable debug output. */

#ifdef LAUNCH_DEBUG
    #if defined(_WIN32) && defined(WINDOWED)
void
mbvs(const char *fmt, ...)
{
    char msg[MBTXTLEN];
    va_list args;
    int pid_len;

    /* Add pid to the message */
    pid_len = sprintf(msg, "[%d] ", getpid());

    va_start(args, fmt);
    vsnprintf(&msg[pid_len], MBTXTLEN-pid_len, fmt, args);
    /* Ensure message is trimmed to fit the buffer. */
    /* msg[MBTXTLEN-1] = '\0'; */
    va_end(args);

    OutputDebugStringA(msg);
}
    #endif /* if defined(_WIN32) && defined(WINDOWED) */
#endif /* ifdef LAUNCH_DEBUG */

#define VPRINTF_TO_STDERR_BUFSIZE (MBTXTLEN * 2)
void vprintf_to_stderr(const char *fmt, va_list v) {
#if defined(_WIN32)
    char utf8_buffer[VPRINTF_TO_STDERR_BUFSIZE];
    char mbcs_buffer[VPRINTF_TO_STDERR_BUFSIZE];

    vsnprintf(utf8_buffer, VPRINTF_TO_STDERR_BUFSIZE, fmt, v);
    if (pyi_win32_utf8_to_mbs(mbcs_buffer,
                              utf8_buffer,
                              VPRINTF_TO_STDERR_BUFSIZE)) {
        fprintf(stderr, "%s", mbcs_buffer);
    }
    else {
        fprintf(stderr, "%s", utf8_buffer);
    }
#else
    vfprintf(stderr, fmt, v);
#endif /* if defined(_WIN32) */
}

void printf_to_stderr(const char* fmt, ...) {
    va_list v;
    va_start(v, fmt);
    vprintf_to_stderr(fmt, v);
    va_end(v);
}

/*
 * Wrap printing debug messages to console.
 */
void
pyi_global_printf(const char *fmt, ...)
{
    va_list v;

    /* Sent 'LOADER text' messages to stderr. */
    fprintf(stderr, "[%d] ", getpid());
    va_start(v, fmt);
    vprintf_to_stderr(fmt, v);
    va_end(v);
    /* For Gui apps on Mac OS X send debug messages also to syslog. */
    /* This allows to see bootloader debug messages in the Console.app log viewer. */
    /* https://en.wikipedia.org/wiki/Console_(OS_X) */
    /* Levels DEBUG and INFO are ignored so use level NOTICE. */
#if defined(__APPLE__) && defined(WINDOWED) && defined(LAUNCH_DEBUG)
    va_start(v, fmt);
    vsyslog(LOG_NOTICE, fmt, v);
    va_end(v);
#endif
}

/*
 * Print a debug message followed by the name of the function that resulted in an error
 * and a textual description of the error, as with perror().
 */
void pyi_global_perror(const char *funcname, const char *fmt, ...) {
    va_list v;

    va_start(v, fmt);
    vprintf_to_stderr(fmt, v);
    va_end(v);
    perror(funcname);  // perror() writes to stderr

    #if defined(__APPLE__) && defined(WINDOWED) && defined(LAUNCH_DEBUG)
        va_start(v, fmt);
            vsyslog(LOG_NOTICE, fmt, v);
            vsyslog(LOG_NOTICE, "%m\n", NULL);  // %m emits the result of strerror()
        va_end(v);
    #endif
}

/*
 * Windows errors.
 *
 * Print a debug message followed by the name of the function that resulted in an error
 * and a textual description of the error, as returned by FormatMessage.
 */
#ifdef _WIN32
void pyi_global_winerror(const char *funcname, const char *fmt, ...) {
    va_list v;

    va_start(v, fmt);
    vprintf_to_stderr(fmt, v);
    va_end(v);
    printf_to_stderr("%s: %s", funcname, GetWinErrorString(GetLastError()));
}
#endif
