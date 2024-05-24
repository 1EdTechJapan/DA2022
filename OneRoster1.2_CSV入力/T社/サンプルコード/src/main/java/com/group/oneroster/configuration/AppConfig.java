package com.group.oneroster.configuration;

import com.opencsv.CSVParser;
import com.opencsv.CSVParserBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

    @Bean
    CSVParser csvParser() {
        return new CSVParserBuilder()
                .withSeparator(',')
                .withQuoteChar('?')
                .withStrictQuotes(false)
                .withIgnoreQuotations(true)
                .build();
    }
}
