/* kolibri-task-multiplexer.h
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

#ifndef KOLIBRI_TASK_MULTIPLEXER_H
#define KOLIBRI_TASK_MULTIPLEXER_H

#include <gio/gio.h>

G_BEGIN_DECLS

#define KOLIBRI_TYPE_TASK_MULTIPLEXER kolibri_task_multiplexer_get_type()
G_DECLARE_FINAL_TYPE(KolibriTaskMultiplexer, kolibri_task_multiplexer, KOLIBRI, TASK_MULTIPLEXER, GObject)

KolibriTaskMultiplexer *kolibri_task_multiplexer_new(void);

GCancellable *kolibri_task_multiplexer_get_cancellable(KolibriTaskMultiplexer *self);

void kolibri_task_multiplexer_cancel(KolibriTaskMultiplexer *self);
gboolean kolibri_task_multiplexer_get_completed(KolibriTaskMultiplexer *self);

void kolibri_task_multiplexer_push_error(KolibriTaskMultiplexer *self,
                                         GError                 *error);
void kolibri_task_multiplexer_push_variant(KolibriTaskMultiplexer *self,
                                           GVariant               *result_variant);

GTask *kolibri_task_multiplexer_add_next(KolibriTaskMultiplexer *self,
                                         GObject                *source_object,
                                         GAsyncReadyCallback callback,
                                         gpointer callback_data);

G_END_DECLS

#endif
