#define F_CPU 8000000UL  // Changed to 8MHz for better I2C performance
#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>

#define BLACK_STEP PD0
#define BLACK_DIR PD1
#define WHITE_STEP PD2
#define WHITE_DIR PD3

#define L_R 0
#define R_L 1
#define B_T 2
#define T_B 3

#define SQUAR_SIZE 52

// I2C commands
#define CMD_L_R 0
#define CMD_R_L 1
#define CMD_B_T 2
#define CMD_T_B 3
#define CMD_STOP 4
#define CMD_CALIBRATE_STEP 5

// I2C slave address
#define SLAVE_ADDRESS 0x08

volatile uint8_t command = 0;
volatile uint8_t distance = 0;
volatile uint8_t data_received = 0;
volatile uint8_t byte_count = 0;

// Your original motor function (corrected)
void step_motor(uint32_t direction, uint32_t distance) {
	// Set direction (1 for CW, 0 for CCW)
	
	float steps = SQUAR_SIZE * distance;
	
	// Set direction pins for both motors based on movement direction
	if(direction == R_L) {
		PORTD |= (1 << WHITE_DIR);   // White motor CW
		PORTD |= (1 << BLACK_DIR);   // Black motor CW
		} else if (direction == L_R) {
		PORTD &= ~(1 << WHITE_DIR);  // White motor CCW
		PORTD &= ~(1 << BLACK_DIR);  // Black motor CCW
		} else if (direction == B_T) {
		PORTD &= ~(1 << BLACK_DIR);  // Black motor CCW
		PORTD |= (1 << WHITE_DIR);   // White motor CW
		} else if(direction == T_B) {
		PORTD &= ~(1 << WHITE_DIR);  // White motor CCW
		PORTD |= (1 << BLACK_DIR);   // Black motor CW
	}

	// Generate steps for both motors simultaneously
	for (uint32_t i = 0; i < steps; i++) {
		// Generate a step pulse on both motors
		PORTD |= (1 << WHITE_STEP);
		PORTD |= (1 << BLACK_STEP);
		_delay_ms(1);               // Step pulse width
		PORTD &= ~(1 << WHITE_STEP);
		PORTD &= ~(1 << BLACK_STEP);
		_delay_ms(1);               // Step interval
	}
}

// Special function for calibration small steps (corrected)
void calibrate_step(uint32_t direction) {
	// Small movement for calibration (like your original calibrate_speed)
	if(direction == R_L) {
		PORTD |= (1 << WHITE_DIR);
		PORTD |= (1 << BLACK_DIR);
		} else if (direction == L_R) {
		PORTD &= ~(1 << WHITE_DIR);
		PORTD &= ~(1 << BLACK_DIR);
		} else if (direction == B_T) {
		PORTD &= ~(1 << BLACK_DIR);
		PORTD |= (1 << WHITE_DIR);
		} else if(direction == T_B) {
		PORTD &= ~(1 << WHITE_DIR);
		PORTD |= (1 << BLACK_DIR);
	}

	// Make only 4 steps (equivalent to calibrate_speed)
	for (uint8_t i = 0; i < 4; i++) {
		PORTD |= (1 << WHITE_STEP);
		PORTD |= (1 << BLACK_STEP);
		_delay_ms(3);  // Slower for calibration
		PORTD &= ~(1 << WHITE_STEP);
		PORTD &= ~(1 << BLACK_STEP);
		_delay_ms(3);
	}
}

// I2C interrupt handler (improved error handling)
ISR(TWI_vect) {
	uint8_t status = TWSR & 0xF8;
	
	
	//debug

	
	switch(status) {
		case 0x60: // SLA+W received, ACK sent
		byte_count = 0;
		TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA) | (1 << TWIE);
		break;

		case 0x80: // Data received, ACK sent
		if (byte_count == 0) {
			command = TWDR;
			byte_count++;
			} else if (byte_count == 1) {
			distance = TWDR;
			data_received = 1;
			byte_count = 0;
		}
		TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA) | (1 << TWIE);
		break;

		case 0xA0: // Stop condition
		TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA) | (1 << TWIE);
		break;

		default:
		TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA) | (1 << TWIE);
		break;

	}
}

void i2c_slave_init() {
	// Configure I2C pins (PC0=SCL, PC1=SDA) as inputs with pull-ups
	DDRC &= ~((1<<PC0) | (1<<PC1));  // Set as inputs
	PORTC |= (1<<PC0) | (1<<PC1);    // Enable pull-ups
	
	// Set I2C bit rate for 100kHz (assuming 8MHz system clock)
	TWBR = 32;  // Bit rate register
	TWSR = 0;   // Prescaler = 1
	
	TWAR = SLAVE_ADDRESS << 1; // Set slave address
	TWCR = (1<<TWINT)|(1<<TWEA)|(1<<TWEN)|(1<<TWIE); // Enable I2C with interrupt
	sei(); // Enable global interrupts
}

int main(void) {
	// Your original pin setup (unchanged)
	DDRD |= (1 << BLACK_DIR) | (1 << BLACK_STEP) | (1 << WHITE_DIR) | (1 <<WHITE_STEP);
	
	// Initialize I2C
	i2c_slave_init();
	
	PORTB ^= (1 << PB0);
	_delay_ms(50);
	while (1) {
		if(data_received) {
			data_received = 0;
			
			switch(command) {
				case CMD_L_R:
				step_motor(L_R, distance);
				break;
				
				case CMD_R_L:
				step_motor(R_L, distance);
				break;
				
				case CMD_B_T:
				step_motor(B_T, distance);
				break;
				
				case CMD_T_B:
				step_motor(T_B, distance);
				break;
				
				case CMD_CALIBRATE_STEP:
				calibrate_step(distance); // distance here is actually direction
				break;
				
				case CMD_STOP:
				// Stop motors (do nothing)
				break;
			}
		}
	}

	return 0;
}