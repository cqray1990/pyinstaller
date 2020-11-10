/*
 * ****************************************************************************
 * Copyright (c) 2020, PyInstaller Development Team.
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
 * Portable macros for converting multi-byte integers from network byte
 * order (big-endian) to host byte order. Based on the public domain
 * portable_endian.h header by Mathias Panzenböck.
 */
#ifndef PYI_ENDIAN_H
#define PYI_ENDIAN_H

#if defined(__linux__) || defined(__CYGWIN__)
#   include <endian.h>
#   define pyi_be16toh(x) be16toh(x)
#   define pyi_be32toh(x) be32toh(x)
#   define pyi_be64toh(x) be64toh(x)
#elif defined(__APPLE__)
#	include <libkern/OSByteOrder.h>
#	define pyi_be16toh(x) OSSwapBigToHostInt16(x)
#	define pyi_be32toh(x) OSSwapBigToHostInt32(x)
#	define pyi_be64toh(x) OSSwapBigToHostInt64(x)
#elif defined(__OpenBSD__)
#	include <sys/endian.h>
#   define pyi_be16toh(x) be16toh(x)
#   define pyi_be32toh(x) be32toh(x)
#   define pyi_be64toh(x) be64toh(x)
#elif defined(__NetBSD__) || defined(__FreeBSD__) || defined(__DragonFly__)
#	include <sys/endian.h>
#	define pyi_be16toh(x) betoh16(x)
#	define pyi_be32toh(x) betoh32(x)
#	define pyi_be64toh(x) betoh64(x)
#elif defined(_WIN32)
#	include <windows.h>
#	if BYTE_ORDER == LITTLE_ENDIAN
#       if defined(_MSC_VER)
#           include <stdlib.h>
#			define pyi_be16toh(x) _byteswap_ushort(x)
#			define pyi_be32toh(x) _byteswap_ulong(x)
#			define pyi_be64toh(x) _byteswap_uint64(x)
#       elif defined(__GNUC__) || defined(__clang__)
#			define pyi_be16toh(x) __builtin_bswap16(x)
#			define pyi_be32toh(x) __builtin_bswap32(x)
#			define pyi_be64toh(x) __builtin_bswap64(x)
#       else
#           error Unsupported platform
#       endif
#   elif BYTE_ORDER == BIG_ENDIAN
#		define pyi_be16toh(x) (x)
#		define pyi_be32toh(x) (x)
#		define pyi_be64toh(x) (x)
#	else
#		error Unsupported byte order
#	endif
#else
#	error Unsupported platform
#endif

#endif
