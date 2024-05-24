public class StringUtil {
    private static final Pattern HALF_WIDTH_KATAKANA = Pattern.compile("[\uff61-\uff9f]");
    private static final Pattern VALID_UUID = Pattern.compile("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-([0-9a-fA-F])[0-9a-fA-F]{3}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");

    /**
     * Validate that one or more string are valid version 4 UUIDs
     * 
     * @param strings
     */
    public static void validateUUIDs(String... strings) {
        for (String s : strings) {
            if (s != null && !s.isEmpty()) {
                Matcher matcher = VALID_UUID.matcher(s);
                if (!matcher.matches()) {
                    throw new HttpNotAllowedException("Invalid UUID " + s);
                }
                String versionDigit = matcher.group(1);
                if (!Objects.equals(versionDigit, "4")) {
                    throw new HttpNotAllowedException("Expected UUID version 4");
                }
            }
        }
    }

    /**
     * Checks whether a UTF-8 string contains any half-width katakana characters
     *
     * @param s The string to test
     * @return
     */
    public static boolean containsHalfWidthKana(String s) {
        return HALF_WIDTH_KATAKANA.matcher(s).find();
    }

    /**
     * Check whether any of a list of strings contain half-width katakana characters
     *
     * @param strings The strings to test
     * @return
     */
    public static boolean anyContainHalfWidthKana(String... strings) {
        for (String s : strings) {
            if (s != null && containsHalfWidthKana(s)) {
                return true;
            }
        }
        return false;
    }
}