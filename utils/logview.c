#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ncurses.h>

#define LOG_FILE "/var/tmp/opencanary.log"
#define MAX_LINES 1000 

void display_latest_entries() {
    FILE *file = fopen(LOG_FILE, "r");
    if (file == NULL) {
        mvprintw(2, 2, "Error opening log file. Press any key to return to menu.");
        getch();
        return;
    }

    char line[1024];
    int count = 0;

    move(0, 0);
    clrtoeol();

    attron(A_BOLD);
    mvprintw(0, 0, "Latest Log Entries:");
    attroff(A_BOLD);

    while (fgets(line, sizeof(line), file) && count < MAX_LINES) {
        mvprintw(count + 1, 0, "%s", line);
        count++;
    }

    fclose(file);
    refresh();
    getch();  
}

void search_events() {
    char keyword[256];

    echo(); 
    mvprintw(2, 2, "Enter search keyword:");
    getstr(keyword);
    noecho(); 

    FILE *file = fopen(LOG_FILE, "r");
    if (file == NULL) {
        mvprintw(4, 2, "Error opening log file. Press any key to return to menu.");
        getch();
        return;
    }

    char line[1024];
    int count = 0;
    int found = 0;

    move(0, 0);
    clrtoeol();

    attron(A_BOLD);
    mvprintw(0, 0, "Search Results for '%s':", keyword);
    attroff(A_BOLD);

    while (fgets(line, sizeof(line), file) && count < MAX_LINES) {
        if (strstr(line, keyword)) {
            mvprintw(count + 1, 0, "%s", line);
            count++;
            found = 1;
        }
    }

    if (!found) {
        mvprintw(count + 1, 0, "No results found for '%s'.", keyword);
    }

    fclose(file);
    refresh();
    getch(); 
}

void filter_by_level() {
    char *log_levels[] = {"src_host", "dst_host", "dst_port"};
    int choice;

    WINDOW *menu_win;
    menu_win = newwin(10, 40, 2, 2);
    box(menu_win, 0, 0);
    mvwprintw(menu_win, 1, 2, "Filter by Log Level:");
    mvwprintw(menu_win, 2, 2, "1. src_host");
    mvwprintw(menu_win, 3, 2, "2. dst_host");
    mvwprintw(menu_win, 4, 2, "3. dst_port");
    mvwprintw(menu_win, 6, 2, "Enter choice (1-3): ");
    wrefresh(menu_win);

    echo();  
    mvwscanw(menu_win, 6, 22, "%d", &choice);
    noecho(); 

    choice--; 

    if (choice >= 0 && choice < sizeof(log_levels) / sizeof(log_levels[0])) {
        FILE *file = fopen(LOG_FILE, "r");
        if (file == NULL) {
            mvprintw(12, 2, "Error opening log file. Press any key to return to menu.");
            getch();
            return;
        }

        char line[1024];
        int count = 0;
        int found = 0;

        move(0, 0);
        clrtoeol();

        attron(A_BOLD);
        mvprintw(0, 0, "Filtered Log Entries (%s):", log_levels[choice]);
        attroff(A_BOLD);

        while (fgets(line, sizeof(line), file) && count < MAX_LINES) {
            if (strstr(line, log_levels[choice])) {
                mvprintw(count + 1, 0, "%s", line);
                count++;
                found = 1;
            }
        }

        if (!found) {
            mvprintw(count + 1, 0, "No %s entries found.", log_levels[choice]);
        }

        fclose(file);
    } else {
        mvprintw(12, 2, "Invalid choice. Press any key to return to menu.");
        getch();
    }

    refresh();
    getch();  
}

int main() {
    initscr(); 
    cbreak();   
    keypad(stdscr, TRUE);  
    start_color(); 

    int choice;
    while (1) {
        clear();  
        mvprintw(0, 0, "CWD Canary Log Monitor");

        mvprintw(2, 2, "1. Display latest log entries");
        mvprintw(3, 2, "2. Search for specific events");
        mvprintw(4, 2, "3. Filter by log level");
        mvprintw(5, 2, "4. Exit");
        mvprintw(7, 2, "Enter choice (1-4): ");
        refresh();

        scanw("%d", &choice);

        switch (choice) {
            case 1:
                display_latest_entries();
                break;
            case 2:
                search_events();
                break;
            case 3:
                filter_by_level();
                break;
            case 4:
                endwin(); 
                return 0;
            default:
                mvprintw(10, 2, "Invalid choice. Press any key to continue.");
                getch();
                break;
        }
    }

    endwin(); 
    return 0;
}
