import gov.adlnet.xapi.client.StatementClient;
import gov.adlnet.xapi.model.*;
import [etc...]

public class EventService {

    private Logger logger = LogManager.getLogger(EventService.class);
    private ExecutorService executorService = Executors.newFixedThreadPool(50);
    private int MAX_EVENT_RETRIES = 3;
    private long BASE_INTERVAL_FOR_RETRIES_MS = 100;
    private static final int MEXCBT_SSO_PROVIDER_ID = 5;
    private static final String MEXCBT_URI = Constants.getStringProperty("mexcbt.xapi.uri");
    private static final String MEXCBT_USERNAME = Constants.getStringProperty("mexcbt.xapi.username");
    private static final String MEXCBT_PASSWORD = Constants.getStringProperty("mexcbt.xapi.password");    
    private static final Activity xAPISourceActivity = new Activity("http://id.tincanapi.com/activity/lrp/lrp name/1.0.0");

    /**
     * If event e is one we send xAPI statements for, and was sent by a MEXCBT user, Build and send an xAPI statement to MEXCBT
     * 
     * @param e An event
     */
    private void sendMEXCBTStatement(Event e) {
        if (e.accountID == null) {
            return;
        }
        dbUserAffiliationEntity affiliation = userAffiliationService.getAffiliation(e.accountID, UserAffiliationType.SSO.getId(), MEXCBT_SSO_PROVIDER_ID);
        if (affiliation != null) {
            Statement s = buildStatementForEvent(e, affiliation.getAlias());
            if (s == null) {
                return;
            }
            if (!StringUtils.isNullOrEmpty(MEXCBT_URI)) {
                try {
                    StatementClient client = new StatementClient(MEXCBT_URI, MEXCBT_USERNAME, MEXCBT_PASSWORD);
                    client.postStatement(s);
                } catch (IOException ex) {
                    logger.error("Failed to post xAPI statement to MEXCBT", ex);
                }
            } else {
                logger.info("MEXCBT xAPI statement:" + s.serialize());
            }
        }
    }

    /**
     * If event e is one we send xAPI statements for, build one. Otherwise, return null.
     * 
     * @param e         An event
     * @param userId    The MEXCBT userMasterIdentifier for the account that sent the event
     * @return
     */
    private Statement buildStatementForEvent(Event e, String userId) {
        if (e instanceof CompleteActivity) {
            Verb verb = Verbs.completed();
            CompleteActivity completeActivity = (CompleteActivity) e;
            Integer activityTypeID = completeActivity.activityTypeID;
            String id = Constants.getStringProperty("url.site") + "/activities/" + completeActivity.activityID;
            ActivityDefinition ad = null;
            Statement statement = buildCoreStatement(e, userId, verb, id, ad, activityTypeID);
            return statement;
        } else if (e instanceof TypedWord || e instanceof TypedQuizWord) {
            DialogWordInteractiveEvent typedWord = (DialogWordInteractiveEvent) e;
            Verb verb = Verbs.answered();
            Integer activityTypeID = typedWord.activityTypeID;
            String id = Constants.getStringProperty("url.site") + "/activities/" + typedWord.activityID + "/word/" + typedWord.word.getWordInstanceID();
            ActivityDefinition ad = new ActivityDefinition();
            ad.setType("http://adlnet.gov/expapi/activities/question");
            ad.setInteractionType("fill-in");
            Statement statement = buildCoreStatement(e, userId, verb, id, ad, activityTypeID);
            Result result = new Result();
            result.setSuccess(typedWord.correct);
            statement.setResult(result);
            return statement;
        } else if (e instanceof QuizzedWord || e instanceof ChosenQuizWord) {
            DialogWordInteractiveEvent quizzedWord = (DialogWordInteractiveEvent) e;
            EventWord chosenWord = e instanceof QuizzedWord ? ((QuizzedWord) e).selectedWord : ((ChosenQuizWord) e).getSelectedWord();
            Verb verb = Verbs.answered();
            Integer activityTypeID = quizzedWord.activityTypeID;
            String id = Constants.getStringProperty("url.site") + "/activities/" + quizzedWord.activityID + "/word/" + quizzedWord.word.getWordInstanceID();
            ActivityDefinition ad = new ActivityDefinition();
            ad.setType("http://adlnet.gov/expapi/activities/question");
            ad.setInteractionType("choice");
            ad.setCorrectResponsesPattern(new ArrayList<>(Collections.singletonList(String.valueOf(quizzedWord.word.getWordInstanceID()))));
            Statement statement = buildCoreStatement(e, userId, verb, id, ad, activityTypeID);
            Result result = new Result();
            result.setSuccess(quizzedWord.correct);
            result.setResponse(String.valueOf(chosenWord.getWordInstanceID()));
            statement.setResult(result);
            return statement;
        } else if (e instanceof DialogLineSpeak) {
            DialogLineSpeak speak = (DialogLineSpeak) e;
            Verb verb = Verbs.interacted();
            Integer activityTypeID = speak.activityTypeID;
            String id = Constants.getStringProperty("url.site") + "/dialogLines/" + speak.dialogLineID;
            ActivityDefinition ad = new ActivityDefinition();
            ad.setType("http://adlnet.gov/expapi/activities/performance");
            ad.setInteractionType("other");
            Statement statement = buildCoreStatement(e, userId, verb, id, ad, activityTypeID);
            Result result = new Result();
            Score score = new Score();
            score.setScaled(speak.score.floatValue());
            result.setScore(score);
            statement.setResult(result);
            return statement;
        }
        return null;
    }

    /**
     * Set up the common parts of a MEXCBT xAPI statement
     * 
     * @param e
     * @param userId
     * @param verb
     * @param activityUri
     * @param ad
     * @param activityTypeID
     * @return
     */
    @NotNull
    private Statement buildCoreStatement(Event e, String userId, Verb verb, String activityUri, ActivityDefinition ad, Integer activityTypeID) {
        Statement statement = new Statement();
        Agent agent = new Agent();
        agent.setAccount(new Account(userId, Constants.getStringProperty("url.site")));
        statement.setVerb(verb);
        statement.setActor(agent);
        statement.setTimestamp(new Date(e.eventTime).toBSON());
        Activity activity = new Activity(activityUri);
        activity.setDefinition(ad);
        statement.setObject(activity);
        ContextActivities contextActivities = new ContextActivities();
        contextActivities.setCategory(new ArrayList<>(getCategoryActivity(activityTypeID)));
        Context context = new Context();
        context.setContextActivities(contextActivities);
        statement.setContext(context);
        return statement;
    }

    /**
     * Build the list of CategoryActivities for an xAPI event for a given activity type
     * @param activityTypeId
     * @return
     */
    private List<Activity> getCategoryActivity(int activityTypeId) {
        // Is this custom category expected to not be here?
        //Activity category = new Activity(Constants.getStringProperty("url.site") + "/activityTypes/" + activityTypeId);
        //category.setDefinition(getCategoryActivityDefinition(activityTypeId));
        return Arrays.asList(xAPISourceActivity);
    }

    /**
     * Build an extra CategoryActivity specifying Company activityTypeId if any (which may not be allowed?)
     * 
     * @param activityType
     * @return
     */
    private ActivityDefinition getCategoryActivityDefinition(int activityType) {
        if (!xAPIActivityTypeNames.containsKey(activityType)) {
            return null;
        }
        HashMap<String, String> activityTypeName = new HashMap<>();
        activityTypeName.put("en", xAPIActivityTypeNames.get(activityType));
        ActivityDefinition definition = new ActivityDefinition(activityTypeName, null);
        definition.setType(xAPIActivityDefinitionTypes.getOrDefault(activityType, "http://adlnet.gov/expapi/activities/performance"));
        return definition;
    }
}