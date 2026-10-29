/*
 * ZeroOS Hardware Abstraction Layer (HAL) Killswitch
 * Feeds digital zeroes (/dev/zero) to microphone PCM streams
 * whenever the target application's sensor register is locked.
 */

#include <hardware/audio.h>
#include <log/log.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

#define LOG_TAG "ZeroOS_AudioKillswitch"

// Checks if the calling UID has an active microphone lock
int is_uid_microphone_locked(uid_t uid) {
    char lock_path[128];
    snprintf(lock_path, sizeof(lock_path), "/data/system/zero_os/mic_locks/%d", uid);
    return (access(lock_path, F_OK) == 0);
}

// In-stream audio filter hook
ssize_t zero_os_audio_read_hook(struct audio_stream_in *stream, void *buffer, size_t bytes, uid_t client_uid) {
    if (is_uid_microphone_locked(client_uid)) {
        // Zero-fill audio buffer: feeds absolute digital silence
        memset(buffer, 0, bytes);
        ALOGV("ZeroOS Audio Killswitch active for UID %d: Feeding zero-amplitude PCM silence", client_uid);
        return bytes;
    }
    // Normal hardware audio capture
    return -1;
}
