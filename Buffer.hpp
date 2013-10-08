#ifndef ___BUFFER__HPP___
#define ___BUFFER__HPP___

#include <istream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


class BufferBase {
public:
    char buffer_[BUFSIZE];
    int continue_;
    char *tokens_;
    size_t linenum_;

    BufferBase() : continue_(0), tokens_(NULL), linenum_(0) {}

    virtual char *get_string(int max_size) = 0;

    char *get_joined_string(int max_size) {
        /* Get an input line, update the line number and cut off *
         * any comment part.  A \ at the end of a line with no   *
         * comment part (#) means continue.                      */

        char *val;
        int i;

        this->continue_ = 0;
        val = this->get_string(max_size);
        this->linenum_++;
        if (val == NULL) return(val);

        /*
        * Check that line completely fit into buffer.  (Flags long line   *
        * truncation).                                                    */

        for (i = 0; i < max_size; i++) {
           if (this->buffer_[i] == '\n')
              break;
           if (this->buffer_[i] == '\0') {
              printf("Error on line %d -- line is too long for input buffer.\n",
                 this->linenum_);
              printf("All lines must be at most %d characters long.\n",
                     BUFSIZE - 2);
              printf("The problem could also be caused by a missing newline.\n");
              exit (1);
           }
        }


        for (i=0;i<max_size && this->buffer_[i] != '\0';i++) {
           if (this->buffer_[i] == '#') {
               this->buffer_[i] = '\0';
               break;
           }
        }

        if (i<2) return (val);
        if (this->buffer_[i - 1] == '\n' && this->buffer_[i - 2] == '\\') {
           this->continue_ = 1;   /* line continued */
           this->buffer_[i - 2] = '\n';  /* May need this for tokens */
           this->buffer_[i - 1] = '\0';
        }
        return(val);
    }

    char *token(char *ptr, char *tokens) {

        /* Get next token, and wrap to next line if \ at end of line.    *
         * There is a bit of a "gotcha" in strtok.  It does not make a   *
         * copy of the character array which you pass by pointer on the  *
         * first call.  Thus, you must make sure this array exists for   *
         * as long as you are using strtok to parse that line.  Don't    *
         * use local buffers in a bunch of subroutines calling each      *
         * other; the local buffer may be overwritten when the stack is  *
         * restored after return from the subroutine.                    */

         char *val;

         val = strtok(ptr, tokens);
         while (1) {
            if (val != NULL || this->continue_ == 0) return(val);
           /* return unless we have a null value and a continuation line */
            if (this->get_joined_string(BUFSIZE) == NULL)
               return(NULL);
            val = strtok(this->buffer_, tokens);
         }
    }
};


class FileBuffer : public BufferBase {
public:
    FILE *fptr_;
    bool close_file_when_done_;

    FileBuffer(char *filename) : BufferBase(), fptr_(NULL),
                                       close_file_when_done_(true) {
        this->fptr_ = my_fopen(filename, "r", 0);
    }

    FileBuffer(FILE *fptr, bool close_file_when_done=true)
            : BufferBase(), fptr_(fptr),
              close_file_when_done_(close_file_when_done) {}

    virtual char *get_string(int max_size) {
        return fgets(this->buffer_, max_size, this->fptr_);
    }

    virtual ~FileBuffer() {
        if(this->close_file_when_done_) {
            fclose(this->fptr_);
        }
    }

};


class StreamBuffer : public BufferBase {
public:
    std::istream *stream_;

    StreamBuffer(std::istream *stream) : BufferBase(), stream_(stream) {}

    virtual char *get_string(int max_size) {
        this->stream_->getline(this->buffer_, max_size);
        return this->buffer_;
    }

};
#endif
