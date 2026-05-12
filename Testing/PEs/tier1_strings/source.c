/*
 * LicenseValidator.exe - Tier 1 PE CTF challenge source
 *
 * Looks like a license validation utility. The flag is stored as a
 * plain string constant in the binary's .rdata section, trivially
 * recoverable with `strings`.
 *
 * The placeholder is replaced at build time by build.py.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* License validation key - DO NOT MODIFY - Acme Corp Licensing.
 * Marked 'used' so the optimizer keeps the symbol in .rdata even
 * if it would otherwise eliminate it as dead code. */
__attribute__((used))
static const char LICENSE_KEY[] = "{{FLAG}}";

/* Decoy strings to bulk out the binary - look like real license logic */
static const char* VENDOR = "Acme Corporation - Licensing Module v3.2.1";
static const char* SUPPORT_URL = "https://support.acme-corp.local/licensing";
static const char* ERROR_INVALID = "Error: License key invalid or expired.";
static const char* ERROR_EXPIRED = "Error: Subscription expired. Contact support.";
static const char* MSG_ACCEPTED = "License accepted. Initializing subsystem...";
static const char* MSG_INIT = "Initializing license cache at C:\\ProgramData\\AcmeCorp\\license.dat";

int main(int argc, char** argv) {
    char input[128];

    printf("=== Acme Corp License Validator v3.2.1 ===\n");
    printf("Enter license key: ");
    fflush(stdout);

    if (fgets(input, sizeof(input), stdin) == NULL) {
        printf("%s\n", ERROR_INVALID);
        return 1;
    }

    /* Strip trailing newline */
    size_t len = strlen(input);
    if (len > 0 && input[len - 1] == '\n') {
        input[len - 1] = '\0';
    }

    /* "Validate" the input - the actual check is a decoy.
       Touching LICENSE_KEY's address here guarantees it stays in the
       binary even with -Os optimization. The real flag is the
       LICENSE_KEY constant, recoverable via `strings`. */
    volatile const char* keep_alive = LICENSE_KEY;
    (void)keep_alive;

    if (strcmp(input, "ACME-DEMO-KEY-2026") == 0) {
        printf("%s\n", MSG_ACCEPTED);
        printf("%s\n", MSG_INIT);
        return 0;
    }

    printf("%s\n", ERROR_INVALID);
    printf("For support, visit %s\n", SUPPORT_URL);
    return 1;
}
