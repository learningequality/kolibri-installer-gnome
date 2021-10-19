/* kolibri-daemon.c
 *
 * Copyright 2021 Endless OS Foundation
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
 * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * Except as contained in this notice, the name(s) of the above copyright
 * holders shall not be used in advertising or otherwise to promote the sale,
 * use or other dealings in this Software without prior written
 * authorization.
 *
 * SPDX-License-Identifier: MIT
 *
 * Author: Dylan McCall <dylan@endlessos.org>
 */

#include <glib.h>
#include <unistd.h>

#include "config.h"

int
main(int argc, char *argv[])
{
  GStrvBuilder *args_builder = NULL;
  GStrv python_args = NULL;

  args_builder = g_strv_builder_new();

  g_strv_builder_add(args_builder, "-m");
  g_strv_builder_add(args_builder, "kolibri_daemon.main");

  for (int idx = 1; idx < argc; idx++)
    {
      g_strv_builder_add(args_builder, argv[idx]);
    }

  python_args = g_strv_builder_end(args_builder);
  g_free(args_builder);

  execv(PYTHON, python_args);
}
