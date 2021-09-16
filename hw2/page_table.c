#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include "page_table_driver.h"

int fd;

// Obtain my cr3 value (a.k.a. PML4 table physical address)
uint64_t get_cr3_value()
{
	struct ioctl_arg cmd;
	int ret;
	cmd.request[0] = IO_CR3;
	ret = ioctl(fd, IOCTL_REQUEST, &cmd);
	return cmd.ret;
}

// Given a physical address, return the value
uint64_t read_physical_address(uint64_t physical_address)
{
	struct ioctl_arg cmd;
	int ret;
	cmd.request[0] = IO_READ;
	cmd.request[1] = physical_address;
	ret = ioctl(fd, IOCTL_REQUEST, &cmd);
	return cmd.ret;
}

// Write value to a physical address
void write_physical_address(uint64_t physical_address, uint64_t value)
{
	struct ioctl_arg cmd;
	int ret;
	cmd.request[0] = IO_WRITE;
	cmd.request[1] = physical_address;
	cmd.request[2] = value;
	ret = ioctl(fd, IOCTL_REQUEST, &cmd);
}

/* get the typical segment from the address */
void divide(uint64_t *addr, uint64_t *offset){
	uint64_t pow = 1;
	for(int i=0; i<9; i++){ // 9 bits
		if(i)
			pow *= 2;
		if(*addr&1)
			*offset += pow;
		*addr = *addr >> 1;
	} 
	
	*offset = *offset << 3; // add three 0 bits at the end
}

/* to get the virtual address's offset */
void get_offset(uint64_t* addr, uint64_t* offset){
	uint64_t pow = 1;
	for(int i=0; i<12; i++){
		if(i)
			pow *= 2;
		if(*addr&1)
			*offset += pow;
		*addr = *addr >> 1;
	} 
}

/* remove the offset of 12 bits */
void remove_offset(uint64_t* addr){
	for(int i=0; i<12; i++)
		*addr = *addr >> 1;
}

/* add the offset of 12 bits which is 0 */
void add_offset(uint64_t* addr){
	for(int i=0; i<12; i++)
		*addr = *addr << 1;
}

/* to get all of the address */
void get_physical_address(uint64_t addr, uint64_t* pt_addr, uint64_t* pd_addr, 
							uint64_t* pdpt_addr, uint64_t* pml4_addr, uint64_t* physical_addr){
	uint64_t pt=0, pd=0, pdpt=0, pml4=0, offset=0;
	
	/* to get the binary segment of the virtual addres */
	get_offset(&addr, &offset);
	divide(&addr, &pt);
	divide(&addr, &pd);
	divide(&addr, &pdpt);
	divide(&addr, &pml4);
	
	/* pml4 */
	*pml4_addr = get_cr3_value()+pml4;
	
	/* pdpt */
	uint64_t content_pml4 = read_physical_address(get_cr3_value()+pml4);
	remove_offset(&content_pml4);
	uint64_t address_pdpt = 0;
	uint64_t pow = 1;
	// to get rid of the higher bits of 80000000
	for(int i=0; i<20; i++){
		if(i)
			pow *= 2;
		if(content_pml4&1)
			address_pdpt += pow;
		content_pml4 = content_pml4>>1;
	}
	add_offset(&address_pdpt);
	address_pdpt += pdpt;
	*pdpt_addr = address_pdpt;
	
	/* pd */
	uint64_t content_pdpt = read_physical_address(address_pdpt);
	uint64_t address_pd = content_pdpt;
	remove_offset(&address_pd);
	add_offset(&address_pd);
	address_pd += pd;
	*pd_addr = address_pd;
	
	/* pt */
	uint64_t content_pd = read_physical_address(address_pd);
	uint64_t address_pt = content_pd;
	remove_offset(&address_pt);
	add_offset(&address_pt);
	address_pt += pt;
	*pt_addr = address_pt;
	
	/* physical address */
	uint64_t content_pt = read_physical_address(address_pt);
	remove_offset(&content_pt);
	uint64_t physical_address = 0;
	pow = 1;
	// to get rid of the higher bits of 80000000
	for(int i=0; i<20; i++){
		if(i)
			pow *= 2;
		if(content_pt&1)
			physical_address += pow;
		content_pt = content_pt>>1;
	}
	add_offset(&physical_address);
	physical_address += offset;
	*physical_addr = physical_address;
}

int main()
{
	char *x = (char*)aligned_alloc(4096, 4096) + 0x123;
	char *y = (char*)aligned_alloc(4096, 4096) + 0x123;
	// printf("x addr: %p\n", (void*)x); // 0x5622fef0b123 -> virtual address
	// printf("y addr: %p\n", (void*)y); // 0x5622fef0d123

	strcpy(x, "This is a simple HW.");
	strcpy(y, "You have to modify my page table.");
	
	fd = open("/dev/os", O_RDONLY);
	if(fd < 0) 
	{
		printf("Cannot open device!\n");
		return 0;
	}
	
	printf("Before\n");
	printf("x : %s\n", x);
	printf("y : %s\n", y);

	/* TODO 1 */
	// ------------------------------------------------
	// Modify page table entry of y
	// Let y point to x's physical address
	// ------------------------------------------------

	/* get the virtual address as uint64_t type */
	uint64_t x_addr = (uint64_t)(void*)x;
	uint64_t y_addr = (uint64_t)(void*)y;
	
	/* get all of the address  */
	uint64_t x_pt_addr, x_pd_addr, x_pdpt_addr, x_pml4_addr, x_physical_addr;
	uint64_t y_pt_addr, y_pd_addr, y_pdpt_addr, y_pml4_addr, y_physical_addr;
	get_physical_address(x_addr, &x_pt_addr, &x_pd_addr, &x_pdpt_addr, &x_pml4_addr, &x_physical_addr);
	get_physical_address(y_addr, &y_pt_addr, &y_pd_addr, &y_pdpt_addr, &y_pml4_addr, &y_physical_addr);
	
	/* store the content what is inside the y_pt_addr for the part2 */
	uint64_t y_pt_content = read_physical_address(y_pt_addr);
	
	/* let y's virtual address point to the physical address same as x */
	write_physical_address(y_pt_addr, read_physical_address(x_pt_addr));
	
	getchar();

	printf("After modifying page table\n");
	printf("x : %s\n", x);
	printf("y : %s\n", y);

	getchar();

	strcpy(y, "When you modify y, x is modified actually.");
	printf("After modifying string y\n");
	printf("x : %s\n", x);
	printf("y : %s\n", y);

	/* TODO 2 */
	// ------------------------------------------------
	// Recover page table entry of y
	// Let y point to its original address
	// You may need to store y's original address at previous step
	// ------------------------------------------------
	write_physical_address(y_pt_addr, y_pt_content);

	getchar();

	printf("After recovering page table of y\n");
	printf("x : %s\n", x);
	printf("y : %s\n", y);

	close(fd);
}
